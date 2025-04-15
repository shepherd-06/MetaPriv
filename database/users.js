const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const dbPath = path.join(__dirname, 'users.db');

/**
 * session management
 */
const { createSession } = require('./session');


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



module.exports = {
    createUser,
    loginUser,
};
