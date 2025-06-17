const path = require('path');
const { v4: uuidv4 } = require('uuid');
const sqlite3 = require('sqlite3').verbose();
const { app } = require('electron');
const fs = require('fs');

const dbDir = app.getPath('userData');
const dbPath = path.join(dbDir, 'users.db');

if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
}

const { validateSession, getMasterPasswordFromSession } = require("./session");
const { aesEncrypt, aesDecrypt } = require('../utility/crypt');

function safeDecrypt(text, masterPassword) {
    try {
        return aesDecrypt(text, masterPassword);
    } catch {
        return text; // Return as-is if decryption fails (likely unencrypted)
    }
}

async function getUsageStats(sessionId) {
    const userId = await validateSession(sessionId);
    if (!userId) {
        throw new Error('Invalid session');
    }

    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (masterPassword === null) {
        console.error("masterPassword returned null from the OS. Abort!");
        return {
            success: false,
            message: "❌ Internal/MasterPassword is null!",
            logs: [],
        };
    }

    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);
        const stats = { userId };

        db.serialize(() => {
            db.get(
                `SELECT username, last_login, created_at FROM users WHERE id = ?`,
                [userId],
                (err, row) => {
                    if (err) return reject(err);
                    stats.userInfo = row || {};

                    db.get(
                        `SELECT COUNT(*) as totalVideos FROM videos WHERE userId = ?`,
                        [userId],
                        (err2, row2) => {
                            if (err2) return reject(err2);
                            stats.totalVideos = row2.totalVideos;

                            db.get(
                                `SELECT COUNT(*) as likedVideos FROM videos WHERE userId = ? AND liked = 1`,
                                [userId],
                                (err3, row3) => {
                                    if (err3) return reject(err3);
                                    stats.likedVideos = row3.likedVideos;
                                    stats.notLikedVideos = stats.totalVideos - stats.likedVideos;

                                    db.all(
                                        `SELECT keyword, COUNT(*) as count FROM videos WHERE userId = ? GROUP BY keyword`,
                                        [userId],
                                        (err4, keywords) => {
                                            if (err4) return reject(err4);

                                            stats.videosByKeyword = keywords.map(k => ({
                                                keyword: safeDecrypt(k.keyword, masterPassword),
                                                count: k.count,
                                            }));

                                            db.all(
                                                `SELECT DATE(watched_at) as date, COUNT(*) as count FROM videos WHERE userId = ? GROUP BY date ORDER BY date DESC LIMIT 10`,
                                                [userId],
                                                (err5, dailyStats) => {
                                                    if (err5) return reject(err5);
                                                    stats.videosWatchedPerDay = dailyStats;

                                                    db.all(
                                                        `SELECT k.id as keywordId, k.text as keyword, p.pageUrl, p.isLiked, p.createdAt, p.updatedAt
                                                         FROM keywords k
                                                         LEFT JOIN pages p ON k.id = p.keywordId
                                                         WHERE k.userId = ?`,
                                                        [userId],
                                                        (err6, keywordPages) => {
                                                            if (err6) return reject(err6);
                                                            stats.keywordPageMap = keywordPages.map(row => ({
                                                                ...row,
                                                                keyword: safeDecrypt(row.keyword, masterPassword),
                                                                pageUrl: safeDecrypt(row.pageUrl, masterPassword),
                                                            }));

                                                            db.all(
                                                                `SELECT page_URL as pageUrl, post_URL as postUrl, liked, watched_at
                                                                 FROM videos
                                                                 WHERE userId = ?`,
                                                                [userId],
                                                                (err7, pageVideos) => {
                                                                    if (err7) return reject(err7);
                                                                    stats.pageVideoMap = pageVideos.map(v => ({
                                                                        ...v,
                                                                        pageUrl: safeDecrypt(v.pageUrl, masterPassword),
                                                                        postUrl: safeDecrypt(v.postUrl, masterPassword),
                                                                    }));

                                                                    db.all(
                                                                        `SELECT 
                                                                            k.id as keywordId,
                                                                            k.text as keyword,
                                                                            posts.postTitle,
                                                                            posts.createdAt,
                                                                            posts.updatedAt
                                                                         FROM keywords k
                                                                         JOIN pages p ON p.keywordId = k.id
                                                                         JOIN posts ON posts.pageId = p.id
                                                                         WHERE k.userId = ? AND posts.isLiked = 1
                                                                         ORDER BY posts.createdAt DESC`,
                                                                        [userId],
                                                                        (err8, likedPostsByKeyword) => {
                                                                            if (err8) return reject(err8);
                                                                            stats.likedPostsByKeyword = likedPostsByKeyword.map(p => ({
                                                                                ...p,
                                                                                keyword: safeDecrypt(p.keyword, masterPassword),
                                                                            }));

                                                                            db.close();
                                                                            resolve(stats);
                                                                        }
                                                                    );
                                                                }
                                                            );
                                                        }
                                                    );
                                                }
                                            );
                                        }
                                    );
                                }
                            );
                        }
                    );
                }
            );
        });
    });
}

module.exports = {
    getUsageStats,
};
