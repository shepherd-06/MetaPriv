const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const dbPath = path.join(__dirname, 'users.db');

const sessions = {}; // In-memory session cache

function createSession(userId) {
    return new Promise((resolve) => {
        const db = new sqlite3.Database(dbPath);
        const id = uuidv4();
        const sessionId = uuidv4(); // can use randomUUID() in newer Node
        const createdAt = new Date().toISOString();
        const expiredAt = new Date(Date.now() + 1000 * 60 * 60 * 12).toISOString(); // expires in 12h

        db.run(
            `INSERT INTO sessions (id, userId, sessionId, createdAt, expiredAt) VALUES (?, ?, ?, ?, ?)`,
            [id, userId, sessionId, createdAt, expiredAt],
            (err) => {
                db.close();
                if (err) {
                    resolve(null);
                } else {
                    resolve(sessionId);
                }
            }
        );
    });
}

function validateSession(sessionId) {
    return new Promise((resolve) => {
        const db = new sqlite3.Database(dbPath);
        db.get(
            `SELECT * FROM sessions WHERE sessionId = ? AND isInvalid = 0`,
            [sessionId],
            (err, row) => {
                db.close();
                if (
                    err ||
                    !row ||
                    new Date(row.expiredAt) < new Date()
                ) {
                    resolve(null); // expired or invalid
                } else {
                    resolve(row.userId); // session is good
                }
            }
        );
    });
}

function invalidateSession(sessionId) {
    return new Promise((resolve) => {
        const db = new sqlite3.Database(dbPath);
        db.run(
            `UPDATE sessions SET isInvalid = 1 WHERE sessionId = ?`,
            [sessionId],
            (err) => {
                db.close();
                resolve(!err);
            }
        );
    });
}

function storeMasterPasswordInSession(sessionId, masterPassword) {
    return new Promise((resolve) => {
        console.log(sessionId, " storeMasterPasswordInSession ", masterPassword);
        if (!sessions[sessionId]) {
            sessions[sessionId] = {};
        }

        sessions[sessionId].masterPassword = masterPassword;
        resolve(true);
    });
}

function getMasterPasswordFromSession(sessionId) {
    return new Promise((resolve) => {
        console.log(sessionId, " getMasterPasswordFromSession");
        resolve(sessions[sessionId]?.masterPassword || null);
    });
}

function clearSession(sessionId) {
    return new Promise((resolve) => {
        console.log(sessionId, " clearSession");
        delete sessions[sessionId];
        resolve(true);
    });
}

module.exports = {
    createSession,
    validateSession,
    invalidateSession,
    storeMasterPasswordInSession,
    getMasterPasswordFromSession,
    clearSession
};