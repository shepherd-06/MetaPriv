const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');

const dbPath = path.join(__dirname, 'users.db');

// Add keywords for a user (array of strings)
async function addKeywords(userId, keywords) {
    const db = new sqlite3.Database(dbPath);
    const now = new Date().toISOString();

    await Promise.all(keywords.map(keyword => {
        return new Promise((resolve, reject) => {
            const id = uuidv4();
            db.run(
                `INSERT INTO keywords (id, userId, keyword, createdAt, isActive)
                 VALUES (?, ?, ?, ?, 1)`,
                [id, userId, keyword, now],
                (err) => {
                    if (err) reject(err);
                    else resolve();
                }
            );
        });
    }));

    db.close();
}

// Get a random active keyword for a user
function getARandomKeyword(userId) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);
        db.all(
            `SELECT keyword FROM keywords WHERE userId = ? AND isActive = 1`,
            [userId],
            (err, rows) => {
                db.close();
                if (err) return reject(err);
                if (!rows || rows.length === 0) return resolve(null);

                const randomIndex = Math.floor(Math.random() * rows.length);
                resolve(rows[randomIndex].keyword);
            }
        );
    });
}

// Disable a specific keyword
function disableKeyword(userId, keyword) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);
        db.run(
            `UPDATE keywords SET isActive = 0 WHERE userId = ? AND keyword = ?`,
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

module.exports = {
    addKeywords,
    getARandomKeyword,
    disableKeyword,
    disableAllKeywords
};
