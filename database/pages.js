const path = require('path');
const { v4: uuidv4 } = require('uuid');
const sqlite3 = require('sqlite3').verbose();
const dbPath = path.join(__dirname, 'users.db');

function addAPage({ keywordId, pageUrl, isLiked = 0 }) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);

        db.get(`SELECT id FROM pages WHERE pageUrl = ?`, [pageUrl], (err, row) => {
            if (err) {
                db.close();
                console.error("Error checking existing page:", err);
                return reject(err);
            }

            if (row) {
                // Page already exists, return success with existing ID
                db.close();
                return resolve({ success: true, id: row.id, existing: true });
            }

            // Otherwise insert new page
            const id = uuidv4();
            const createdAt = new Date().toISOString();

            db.run(
                `INSERT INTO pages (id, keywordId, pageUrl, isLiked, createdAt) VALUES (?, ?, ?, ?, ?)`,
                [id, keywordId, pageUrl, isLiked, createdAt],
                function (insertErr) {
                    db.close();
                    if (insertErr) {
                        console.error("Error adding page:", insertErr);
                        return reject(insertErr);
                    } else {
                        return resolve({ success: true, id, existing: false });
                    }
                }
            );
        });
    });
}


function getARandomPageUrl(isLiked = 0) {
    /**
     * gets a random page URL, if the page is already liked or not liked.
     * 
     */
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);

        db.all(
            `SELECT pageUrl FROM pages WHERE isLiked = ?`,
            [isLiked],
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

function markPageAsLiked(pageUrl) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);
        const updatedAt = new Date().toISOString();

        db.run(
            `UPDATE pages SET isLiked = 1, updatedAt = ? WHERE pageUrl = ?`,
            [updatedAt, pageUrl],
            function (err) {
                db.close();
                if (err) {
                    console.error("Error updating page like status:", err);
                    return reject(err);
                }

                if (this.changes === 0) {
                    // No page found to update
                    return resolve({ success: false, message: 'Page not found.' });
                }

                return resolve({ success: true, message: 'Page marked as liked.' });
            }
        );
    });
}


module.exports = {
    addAPage,
    getARandomPageUrl,
    disableAPage,
    markPageAsLiked
}