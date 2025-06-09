const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');

const { app } = require('electron');
const fs = require('fs');

const dbDir = app.getPath('userData');
const dbPath = path.join(dbDir, 'users.db');

// Ensure the directory exists (just in case)
if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
}

const { validateSession } = require("./session");

const { aesEncrypt, aesDecrypt } = require('../utility/crypt');
const { writeLog } = require('../utility/logmanager');

// Add keywords for a user (array of strings)/
async function addKeywordsForUser(userId, keywords, masterPassword) {
    const db = new sqlite3.Database(dbPath);
    const now = new Date().toISOString();

    try {
        // Clean up keywords first (lowercase + trim)
        const cleanedKeywords = keywords.map(kw => kw.trim().toLowerCase()).filter(kw => kw.length > 0);
        // encrypt all keywords
        const encryptedKeywords = cleanedKeywords.map(kw => aesEncrypt(kw, masterPassword));

        // only enter encrypted keywords that are not already in the database
        await Promise.all(encryptedKeywords.map(keyword => {
            return new Promise((resolve, reject) => {
                // First, check if the keyword already exists for this user
                db.get(
                    `SELECT id FROM keywords WHERE userId = ? AND text = ?`,
                    [userId, keyword],
                    (err, row) => {
                        if (err) {
                            return reject(err);
                        }

                        if (row) {
                            // Keyword already exists - skip adding
                            console.log(`Keyword already exists: ${keyword}`);
                            return resolve();
                        }

                        // Otherwise, insert new keyword
                        const id = uuidv4();
                        db.run(
                            `INSERT INTO keywords (id, userId, text, createdAt, isActive)
                             VALUES (?, ?, ?, ?, 1)`,
                            [id, userId, keyword, now],
                            (insertErr) => {
                                if (insertErr) reject(insertErr);
                                else resolve();
                            }
                        );
                    }
                );
            });
        }));

        db.close();
        return true;  // SUCCESS
    } catch (error) {
        db.close();
        console.error("❌ Failed to add keywords:", error);
        return false; // FAILURE
    }
}



// Get a random active keyword for a user
function getARandomKeyword(userId, masterPassword) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);
        db.all(
            `SELECT id, text FROM keywords WHERE userId = ? AND isActive = 1`,
            [userId],
            (err, rows) => {
                db.close();
                if (err) return reject(err);
                if (!rows || rows.length === 0) return resolve(null);

                const randomIndex = Math.floor(Math.random() * rows.length);
                let decrypted;
                try {
                    decrypted = aesDecrypt(rows[randomIndex].text, masterPassword);
                } catch (e) {
                    writeLog(`⚠️ Failed to decrypt keyword with id ${row.id}: ${e.message}`, masterPassword);
                    decrypted = rows[randomIndex].text; // fallback to encrypted
                }
                resolve({
                    keyword: decrypted,
                    id: rows[randomIndex].id
                });
            }
        );
    });
}

// Disable a specific keyword
function disableKeyword(userId, keyword) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);
        db.run(
            `UPDATE keywords SET isActive = 0 WHERE userId = ? AND text = ?`,
            [userId, keyword],
            function (err) {
                db.close();
                if (err) reject(err);
                else resolve(this.changes > 0); // true if something was updated
            }
        );
    });
}

// Disable all active keywords for a user
function disableAllKeywords(userId) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);
        db.run(
            `UPDATE keywords SET isActive = 0 WHERE userId = ? AND isActive = 1`,
            [userId],
            function (err) {
                db.close();
                if (err) reject(err);
                else resolve(this.changes > 0);
            }
        );
    });
}

function fetchKeywordsForUser(userId, masterPassword) {
    return new Promise((resolve) => {
        const db = new sqlite3.Database(dbPath);

        db.all(
            `SELECT id, text, isActive, createdAt FROM keywords WHERE userId = ? ORDER BY createdAt DESC`,
            [userId],
            (err, rows) => {
                db.close();
                if (err) {
                    console.error("Error fetching keywords:", err);
                    resolve([]);
                } else {
                    const result = rows.map(row => {
                        let decrypted;
                        try {
                            decrypted = aesDecrypt(row.text, masterPassword);
                        } catch (e) {
                            writeLog(`⚠️ Failed to decrypt keyword with id ${row.id}: ${e.message}`, masterPassword);
                            decrypted = row.text; // fallback to encrypted
                        }

                        return {
                            id: row.id,
                            text: decrypted,
                            isActive: row.isActive,
                            createdAt: row.createdAt
                        };
                    });

                    resolve(result);
                }
            }
        );
    });
}

function count(userId) {
    return new Promise((resolve) => {
        const db = new sqlite3.Database(dbPath);

        db.get(
            `SELECT COUNT(*) as count FROM keywords WHERE userId = ?`,
            [userId],
            (err, row) => {
                db.close();
                if (err) {
                    console.error("Error counting keywords:", err);
                    resolve(0);
                } else {
                    resolve(row.count);
                }
            }
        );
    });
}

async function fetchAllKeywords(sessionId, masterPassword) {
    const userId = await validateSession(sessionId);
    if (!userId) {
        return {
            success: false,
            message: '❌ Invalid session. Please log in again.',
            keywords: [],
        };
    }

    const keywords = await fetchKeywordsForUser(userId, masterPassword);

    return {
        success: true,
        message: `✅ Retrieved ${keywords.length} keywords successfully.`,
        keywords: keywords, // array of { id, text, isActive, createdAt }
    };
}


async function addKeywords(sessionId, keywords, masterPassword) {
    const userId = await validateSession(sessionId);
    if (!userId) {
        return {
            success: false,
            message: '❌ Invalid session. Please log in again.',
        };
    }

    const result = await addKeywordsForUser(userId, keywords, masterPassword);

    if (result) {
        return {
            success: true,
            message: '✅ Keywords added successfully!',
        };
    } else {
        return {
            success: false,
            message: '❌ Failed to add keywords!',
        };
    }
}

async function numberOfKeywords(userId) {
    const countResult = await count(userId);
    if (countResult === 0) {
        return {
            success: false,
            message: '❌ No keywords found for this user.',
        };
    }
    return {
        success: true,
        message: `✅ Found ${countResult} keywords.`,
    };
}



module.exports = {
    fetchAllKeywords,
    addKeywords,
    getARandomKeyword,
    numberOfKeywords
};
