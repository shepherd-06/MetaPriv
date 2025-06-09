const path = require('path');
const { v4: uuidv4 } = require('uuid');
const sqlite3 = require('sqlite3').verbose();
const { app } = require('electron');
const fs = require('fs');

const dbDir = app.getPath('userData');
const dbPath = path.join(dbDir, 'users.db');

// Ensure the directory exists (just in case)
if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
}

/** 
 * All hail to encryption and decryption 
 * and logging. but logging is secondary :p
*/
const { aesEncrypt, aesDecrypt } = require('../utility/crypt');
const { writeLog } = require('../utility/logmanager');

function insertPost(pageUrl, postTitle, isLiked = 0, masterPassword) {
    const db = new sqlite3.Database(dbPath);
    const postId = uuidv4();
    const createdAt = new Date().toISOString();
    const encryptedPageUrl = aesEncrypt(pageUrl, masterPassword);

    db.get(
        `SELECT id FROM pages WHERE pageUrl = ?`,
        [encryptedPageUrl],
        (err, row) => {
            if (err) {
                console.error('❌ Error querying pages:', err.message);
                db.close();
                return;
            }

            if (!row) {
                console.error('❌ No matching page found for URL:', pageUrl);
                db.close();
                return;
            }

            const pageId = row.id;

            db.run(
                `INSERT INTO posts (id, pageId, postTitle, isLiked, createdAt) VALUES (?, ?, ?, ?, ?)`,
                [postId, pageId, postTitle, isLiked, createdAt],
                function (err) {
                    if (err) {
                        console.error('❌ Error inserting post:', err.message);
                    } else {
                        console.log(`✅ Post inserted with ID: ${postId}`);
                    }
                    db.close();
                }
            );
        }
    );
}

module.exports = {
    insertPost,
};