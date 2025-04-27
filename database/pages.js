const path = require('path');
const { v4: uuidv4 } = require('uuid');
const sqlite3 = require('sqlite3').verbose();
const dbPath = path.join(__dirname, 'users.db');

function addAPage({ keywordId, pageUrl, isLiked = 0 }) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);
        const id = uuidv4();
        const createdAt = new Date().toISOString();

        db.run(
            `INSERT INTO pages (id, keywordId, pageUrl, isLiked, createdAt) VALUES (?, ?, ?, ?, ?)`,
            [id, keywordId, pageUrl, isLiked, createdAt],
            function (err) {
                db.close();
                if (err) {
                    console.error("Error adding page:", err);
                    reject(err);
                } else {
                    resolve({ success: true, id });
                }
            }
        );
    });
}

function getARandomPageUrl(keywordId) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);

        db.all(
            `SELECT pageUrl FROM pages WHERE keywordId = ? AND isLiked = 1`,
            [keywordId],
            (err, rows) => {
                db.close();
                if (err) {
                    console.error("Error fetching pages:", err);
                    reject(err);
                } else if (rows.length === 0) {
                    resolve(null);
                } else {
                    const randomRow = rows[Math.floor(Math.random() * rows.length)];
                    resolve(randomRow.pageUrl);
                }
            }
        );
    });
}

function disableAPage(pageUrl) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);
        const updatedAt = new Date().toISOString();

        db.run(
            `UPDATE pages SET isLiked = 0, updatedAt = ? WHERE pageUrl = ?`,
            [updatedAt, pageUrl],
            function (err) {
                db.close();
                if (err) {
                    console.error("Error disabling page:", err);
                    reject(err);
                } else {
                    resolve({ success: true });
                }
            }
        );
    });
}


module.exports = {
    addAPage,
    getARandomPageUrl,
    disableAPage
}