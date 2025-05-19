const { v4: uuidv4 } = require("uuid");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");

const dbPath = path.join(__dirname, "users.db"); // adjust if your path is different

function addAVideo({
    post_URL,
    page_URL,
    keyword,
    userId,
    screenshot_name = "",
    liked = 0,
    watchTime = 0,
}) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);
        const id = uuidv4();
        const time = new Date().toISOString();

        db.run(
            `INSERT INTO videos (id, post_URL, page_URL, keyword, userId, liked, time, screenshot_name, watchTime)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
            [id, post_URL, page_URL, keyword, userId, liked, time, screenshot_name, watchTime],
            function (err) {
                db.close();

                if (err) {
                    console.error("❌ Error adding video:", err.message);
                    return resolve({
                        success: false,
                        id: null,
                        message: "Failed to add video.",
                    });
                }

                return resolve({
                    success: true,
                    id,
                    message: "✅ Video added successfully!",
                });
            }
        );
    });
}

module.exports = {
    addAVideo,
};
