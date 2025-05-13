const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const dbPath = path.join(__dirname, 'users.db');
const axios = require('axios');

const { writeLog } = require('../utility/logmanager');

// Helper: run an SQL write (INSERT/UPDATE) as a promise
function runQuery(sql, params = []) {
    const db = new sqlite3.Database(dbPath);
    return new Promise((resolve, reject) => {
        db.run(sql, params, function (err) {
            db.close();
            if (err) reject(err);
            else resolve(this);
        });
    });
}

// Helper: run an SQL read (SELECT) as a promise
function getQuery(sql, params = []) {
    const db = new sqlite3.Database(dbPath);
    return new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => {
            db.close();
            if (err) reject(err);
            else resolve(row);
        });
    });
}

// Function 1: Fetch sync status
async function fetchSyncStatus(userId) {
    try {
        const row = await getQuery(
            `SELECT backendUrl, syncFrequency FROM syncConfigs WHERE userId = ?`,
            [userId]
        );
        if (row) {
            return {
                success: true,
                backendUrl: row.backendUrl,
                syncPeriod: row.syncFrequency
            };
        } else {
            return {
                success: false,
                message: 'No sync settings found for this user.'
            };
        }
    } catch (err) {
        console.error('Error in fetchSyncStatus:', err);
        return {
            success: false,
            message: `Error fetching sync status: ${err.message}`
        };
    }
}

// Function 2: Enable user sync status
async function enableUserSyncStatus(userId) {
    try {
        await runQuery(
            `UPDATE users SET isSync = 1 WHERE id = ?`,
            [userId]
        );
        return { success: true };
    } catch (err) {
        console.error('Error in enableUserSyncStatus:', err);
        return {
            success: false,
            message: `Error enabling user sync: ${err.message}`
        };
    }
}

// Function 3: Save sync status
async function saveSyncStatus(userId, backendUrl, syncPeriod) {
    try {
        const enableResult = await enableUserSyncStatus(userId);
        if (!enableResult.success) {
            return enableResult;
        }

        await runQuery(
            `
            INSERT INTO syncConfigs (userId, backendUrl, syncFrequency, createdAt, updatedAt, backendStatus)
            VALUES (?, ?, ?, datetime('now'), datetime('now'), 200)
            ON CONFLICT(userId) DO UPDATE SET
                backendUrl = excluded.backendUrl,
                syncFrequency = excluded.syncFrequency,
                updatedAt = datetime('now'),
                backendStatus = 200;
            `,
            [userId, backendUrl, syncPeriod]
        );

        return { success: true, message: 'Sync settings saved successfully.' };
    } catch (err) {
        console.error('Error in saveSyncStatus:', err);
        return {
            success: false,
            message: `Error saving sync status: ${err.message}`
        };
    }
}

// Function 4: Run SYNC.
// Main runner
async function runSyncForUser(userId, masterPassword) {
    try {
        // 1. Check if sync is enabled for this user
        const user = await getQuery(`SELECT isSync FROM users WHERE id = ?`, [userId]);
        if (!user || user.isSync !== 1) {
            writeLog(`❌ Sync is not enabled for this user. ${userId}`, masterPassword);
            return { success: false, message: '❌ Sync is not enabled for this user.' };
        }

        // 2. Fetch sync config
        const config = await getQuery(`SELECT * FROM syncConfigs WHERE userId = ?`, [userId]);
        if (!config || !config.backendUrl) {
            writeLog(`❌ Sync config missing or invalid for userId: ${userId}`, masterPassword);
            return { success: false, message: '❌ Sync config missing or invalid.' };
        }

        // 3. Perform sync operations
        const backendUrl = config.backendUrl;
        let keywordResult = null;
        let pageResult = null;
        let videoResult = null;
        const userResult = await syncUser(userId, backendUrl, masterPassword);

        if (userResult.success === true) {
            keywordResult = await syncKeywords(userId, backendUrl, masterPassword);
            pageResult = await syncPages(userId, backendUrl, masterPassword);
            videoResult = await syncVideos(userId, backendUrl, masterPassword);

            return {
                success: true,
                message: '✅ Sync complete',
                results: {
                    user: userResult,
                    keywords: keywordResult,
                    pages: pageResult,
                    videos: videoResult,
                }
            };
        } else {
            return {
                success: userResult.success,
                message: `❌ Error syncing! ${userResult.message}`,
                results: {
                    user: userResult,
                    keywords: keywordResult,
                    pages: pageResult,
                    videos: videoResult,
                }
            };
        }
    } catch (err) {
        writeLog(`❌ Error in runSyncForUser: ${err.message}`, masterPassword);
        return {
            success: false, message: err.message, results: {
                user: null,
                keywords: null,
                pages: null,
                videos: null
            }
        };
    }
}

// sync queue: 4
async function syncVideos(userId, backendUrl, masterPassword) {
    const db = new sqlite3.Database(dbPath);

    return new Promise((resolve, reject) => {
        db.all(
            `SELECT * FROM videos WHERE userId = ? ORDER BY datetime(time) DESC`,
            [userId],
            async (err, rows) => {
                db.close();
                if (err) {
                    return reject({
                        success: false,
                        message: 'DB read error',
                        error: err
                    });
                }

                if (!rows || rows.length === 0) {
                    return resolve({ success: true, message: 'No videos to sync.' });
                }

                try {
                    const payload = rows.map(row => ({
                        app_id: row.id,
                        post_URL: row.post_URL,
                        page_URL: row.page_URL,
                        keyword: row.keyword,
                        user_id: row.userId,
                        liked: row.liked,
                        time: row.time,
                        screenshot_name: row.screenshot_name,
                        watched_at: row.watched_at
                    }));

                    const response = await axios.post(`${backendUrl}sync/videos`, payload);
                    const statusCode = response.status;
                    const { message, inserted_app_ids } = response.data;

                    if (statusCode === 201) {
                        const latestId = inserted_app_ids?.[inserted_app_ids.length - 1] || rows[0].id;

                        await runQuery(
                            `UPDATE syncConfigs SET lastVideoSyncId = ?, updatedAt = datetime('now') WHERE userId = ?`,
                            [latestId, userId]
                        );
                    }

                    resolve({
                        success: statusCode === 201,
                        message: `✅ Synced ${inserted_app_ids.length} videos.`,
                        inserted_app_ids,
                        status: statusCode
                    });

                } catch (error) {
                    let errorResult;

                    if (error.response) {
                        errorResult = {
                            success: false,
                            status: error.response.status,
                            message: error.response.data?.message || '❌ Server error during video sync',
                            error: error.response.data?.error || null
                        };
                    } else if (error.request) {
                        errorResult = {
                            success: false,
                            message: '❌ No response from server',
                            status: null
                        };
                    } else {
                        errorResult = {
                            success: false,
                            message: `❌ Unexpected error: ${error.message}`,
                            status: null
                        };
                    }

                    writeLog(`Video sync failed: ${errorResult.message}`, masterPassword);
                    resolve(errorResult); // use resolve to avoid crashing sync pipeline
                }
            }
        );
    });
}

// sync queue: 2
async function syncKeywords(userId, backendUrl, masterPassword) {
    const db = new sqlite3.Database(dbPath);

    return new Promise((resolve, reject) => {
        db.all(
            `SELECT * FROM keywords WHERE userId = ? ORDER BY createdAt DESC`,
            [userId],
            async (err, rows) => {
                db.close();
                if (err) return reject({ success: false, message: 'DB read error', error: err });

                if (!rows || rows.length === 0) return resolve({ success: true, message: 'No keywords to sync.' });

                try {
                    const payload = rows.map(row => ({
                        app_id: row.id,
                        user_id: row.userId,
                        text: row.text,
                        is_active: row.isActive,
                        created_at: row.createdAt
                    }));

                    const response = await axios.post(`${backendUrl}sync/keywords`, payload);
                    const statusCode = response.status;
                    const { message, inserted_app_ids } = response.data;

                    if (statusCode === 201) {
                        if (inserted_app_ids.length !== 0) {
                            const latestId = rows[0].id;
                            await runQuery(
                                `UPDATE syncConfigs SET lastKeywordSyncId = ?, updatedAt = datetime('now') WHERE userId = ?`,
                                [latestId, userId]
                            );
                        }
                    }

                    return resolve({
                        success: statusCode === 201,
                        message: `✅ Synced ${inserted_app_ids.length} keywords.`,
                        inserted_app_ids,
                        status: statusCode
                    });
                } catch (error) {
                    let errorResult;

                    if (error.response) {
                        errorResult = {
                            success: false,
                            message: error.response.data?.message || '❌ Sync failed with server error',
                            error: error.response.data?.error || null,
                            status: error.response.status
                        };
                    } else if (error.request) {
                        errorResult = {
                            success: false,
                            message: '❌ No response from server',
                            status: null
                        };
                    } else {
                        errorResult = {
                            success: false,
                            message: `❌ Unexpected error: ${error.message}`,
                            status: null
                        };
                    }

                    writeLog(`Keyword sync failed: ${errorResult.message}`, masterPassword);
                    return resolve(errorResult); // resolve even if failed, not reject, to keep flow clean
                }
            }
        );
    });
}


// sync queue: 3
async function syncPages(userId, backendUrl, masterPassword) {
    const db = new sqlite3.Database(dbPath);

    return new Promise((resolve, reject) => {
        db.all(
            `SELECT * FROM pages WHERE keywordId IN (
                SELECT id FROM keywords WHERE userId = ?
            ) ORDER BY datetime(COALESCE(updatedAt, createdAt)) DESC`,
            [userId],
            async (err, rows) => {
                db.close();
                if (err) {
                    return reject({
                        success: false,
                        message: 'DB read error',
                        error: err
                    });
                }

                if (!rows || rows.length === 0) {
                    return resolve({
                        success: true,
                        message: 'No pages to sync.'
                    });
                }

                try {
                    const payload = rows.map(row => ({
                        app_id: row.id,
                        keyword_id: row.keywordId,
                        page_url: row.pageUrl,
                        is_liked: row.isLiked,
                        created_at: row.createdAt,
                        updated_at: row.updatedAt
                    }));

                    const response = await axios.post(`${backendUrl}sync/pages`, payload);
                    const statusCode = response.status;
                    const { message, inserted_app_ids } = response.data;

                    if (statusCode === 201) {
                        if (inserted_app_ids.length !== 0) {
                            const latestId = inserted_app_ids?.[inserted_app_ids.length - 1] || rows[0].id;
                            await runQuery(
                                `UPDATE syncConfigs SET lastPageSyncId = ?, updatedAt = datetime('now') WHERE userId = ?`,
                                [latestId, userId]
                            );
                        }
                    }

                    resolve({
                        success: statusCode === 201,
                        message: `✅ Synced ${inserted_app_ids.length} pages.`,
                        status: statusCode
                    });

                } catch (error) {
                    let errorResult;

                    if (error.response) {
                        errorResult = {
                            success: false,
                            status: error.response.status,
                            message: error.response.data?.message || '❌ Server error during page sync',
                            error: error.response.data?.error || null
                        };
                    } else if (error.request) {
                        errorResult = {
                            success: false,
                            message: '❌ No response from server',
                            status: null
                        };
                    } else {
                        errorResult = {
                            success: false,
                            message: `❌ Unexpected error: ${error.message}`,
                            status: null
                        };
                    }

                    writeLog(`Page sync failed: ${errorResult.message}`, masterPassword);
                    resolve(errorResult); // Use resolve for uniform return flow
                }
            }
        );
    });
}

// sync queue: 1
async function syncUser(userId, backendUrl, masterPassword) {
    try {
        const user = await getQuery(
            `SELECT id, username, password, created_at, updated_at, last_login FROM users WHERE id = ?`,
            [userId]
        );

        if (!user) {
            return {
                success: false,
                message: '❌ User not found.',
                status: 404
            };
        }

        const payload = {
            id: user.id,
            username: user.username,
            password: user.password, // assumed hashed
            created_at: user.created_at,
            updated_at: user.updated_at,
            last_login: user.last_login
        };

        const response = await axios.post(`${backendUrl}sync/user`, payload);
        const statusCode = response.status;
        const responseMessage = response.data?.message || '✅ User synced.';

        return {
            success: statusCode === 201,
            status: statusCode,
            message: responseMessage
        };

    } catch (error) {
        let status = null;
        let message = '❌ Unknown error occurred during user sync';

        if (error.response) {
            // Backend returned a non-2xx status
            status = error.response.status;
            message = error.response.data?.message || '❌ Server error during user sync';
        } else if (error.request) {
            message = '❌ No response from backend server';
        } else {
            message = `❌ Error: ${error.message}`;
        }

        writeLog(`User sync failed: ${message}`, masterPassword);

        return {
            success: false,
            status,
            message
        };
    }
}


// Export functions at the bottom
module.exports = {
    fetchSyncStatus,
    enableUserSyncStatus,
    saveSyncStatus,
    runSyncForUser,
};
