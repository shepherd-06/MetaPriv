const path = require('path');
const { v4: uuidv4 } = require('uuid');
const sqlite3 = require('sqlite3').verbose();
const dbPath = path.join(__dirname, 'users.db');

function insertPost(pageUrl, postTitle, isLiked = 0) {
    const db = new sqlite3.Database(dbPath);
    const postId = uuidv4();
    const createdAt = new Date().toISOString();

    db.get(
        `SELECT id FROM pages WHERE pageUrl = ?`,
        [pageUrl],
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