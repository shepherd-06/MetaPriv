const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const dbPath = path.join(__dirname, 'users.db');

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

// Export functions at the bottom
module.exports = {
    fetchSyncStatus,
    enableUserSyncStatus,
    saveSyncStatus
};
