const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const dbPath = path.join(__dirname, 'users.db');

// Ensure DB and users table exist
function initUserTable() {
    const db = new sqlite3.Database(dbPath);
    db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      username TEXT UNIQUE,
      password TEXT,
      masterPassword TEXT DEFAULT NULL,
      fbEmail TEXT DEFAULT NULL,
      created_at TEXT,
      updated_at TEXT,
      last_login TEXT
    );
  `);
    db.close();
}

function initSessionTable() {
    const db = new sqlite3.Database(dbPath);
    db.run(`
    CREATE TABLE IF NOT EXISTS sessions (
      id TEXT PRIMARY KEY,
      userId TEXT,
      sessionId TEXT,
      createdAt TEXT,
      expiredAt TEXT,
      isInvalid INTEGER DEFAULT 0,
      FOREIGN KEY(userId) REFERENCES users(id)
    );
  `);
    db.close();
}

// Create a new user
function createUser({ username, password }) {
    return new Promise(async (resolve) => {
        const db = new sqlite3.Database(dbPath);
        const id = uuidv4();
        const hashedPassword = await bcrypt.hash(password, 10);
        const timestamp = new Date().toISOString();

        db.run(
            `INSERT INTO users (id, username, password, created_at, updated_at) VALUES (?, ?, ?, ?, ?)`,
            [id, username, hashedPassword, timestamp, timestamp],
            (err) => {
                if (err) {
                    resolve({ success: false, message: '❌ Username already exists or DB error.' });
                } else {
                    resolve({
                        success: true,
                        message: '✅ Account created successfully! Please login!',
                    });
                }
                db.close();
            }
        );
    });
}

// Login a user
function loginUser({ username, password }) {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath);
        db.get(
            `SELECT * FROM users WHERE username = ?`,
            [username],
            async (err, row) => {
                if (err || !row) {
                    db.close();
                    return resolve({ success: false, message: '❌ Invalid credentials.' });
                }

                const match = await bcrypt.compare(password, row.password);
                if (!match) {
                    db.close();
                    return resolve({ success: false, message: '❌ Invalid credentials.' });
                }

                const now = new Date().toISOString();
                db.run(`UPDATE users SET last_login = ? WHERE id = ?`, [now, row.id]);

                // Create session
                const sessionId = await createSession(row.id);
                if (!sessionId) {
                    db.close();
                    return resolve({ success: false, message: '❌ Failed to create session.' });
                }

                // Determine onboarding step
                let onboardingStep = 2;
                if (row.masterPassword) onboardingStep = 3;
                if (row.masterPassword && row.fbEmail) onboardingStep = 4;

                db.close();
                resolve({
                    success: true,
                    message: '✅ Logged in!',
                    sessionId,
                    onboardingStep
                });
            }
        );
    });
}


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


module.exports = {
    initUserTable,
    initSessionTable,
    createUser,
    loginUser,
    createSession,
    validateSession,
    invalidateSession
};
