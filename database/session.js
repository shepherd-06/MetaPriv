const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const dbPath = path.join(__dirname, 'users.db');

const keytar = require('keytar');
const SERVICE_NAME = 'MetaPriv.MasterPassword'; // You can change this to whatever your app's name is


function createSession(userId) {
    return new Promise((resolve) => {
        const db = new sqlite3.Database(dbPath);
        const id = uuidv4();
        const sessionId = uuidv4(); // can use randomUUID() in newer Node
        const createdAt = new Date().toISOString();
        // const expiredAt = new Date(Date.now() + 1000 * 60 * 60 * 12).toISOString(); // expires in 12h
        const expiredAt = new Date(Date.now() + 1000 * 60 * 60 * 24 * 7).toISOString(); // expires in 7 days

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

async function storeMasterPasswordInSession(userId, masterPassword) {
    try {
        await keytar.setPassword(SERVICE_NAME, userId, masterPassword);
        return true;
    } catch (error) {
        console.error("Error storing master password:", error);
        return false;
    }
}

async function getMasterPasswordFromSession(sessionId) {
    try {
        const userId = await validateSession(sessionId);
        if (!userId) {
            console.error("❌ Invalid or expired session. ", sessionId);
            return null;
        }

        const password = await keytar.getPassword(SERVICE_NAME, userId);
        return password || null;
    } catch (error) {
        console.error("Error retrieving master password:", error);
        return null;
    }
}


async function clearSession(sessionId) {
    try {
        await keytar.deletePassword(SERVICE_NAME, sessionId);
        console.log(`${sessionId} cleared from keychain.`);
        return true;
    } catch (error) {
        console.error("Error clearing session:", error);
        return false;
    }
}


module.exports = {
    createSession,
    validateSession,
    invalidateSession,
    storeMasterPasswordInSession,
    getMasterPasswordFromSession,
    clearSession
};