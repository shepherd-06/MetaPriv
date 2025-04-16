const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const dbPath = path.join(__dirname, 'users.db');
/**
 * session management
 */
const { createSession, storeMasterPasswordInSession, validateSession } = require('./session');


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
                if (row.masterPassword && !row.fbEmail) onboardingStep = 3;
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

function validateMasterPassword(password) {
    if (password.length !== 24) {
        return 'Password must be exactly 24 characters long.';
    }
    if (!/[a-zA-Z]/.test(password)) {
        return 'Password must contain at least one letter.';
    }
    if (!/\d/.test(password)) {
        return 'Password must contain at least one number.';
    }
    if (!/[\W_]/.test(password)) {
        return 'Password must contain at least one special character.';
    }
    return null;
}

// Set master password (data = { sessionId, masterPassword })
function setMasterPassword({ sessionId, masterPassword }) {
    return new Promise(async (resolve) => {
        // Step 1: Check if the sessionId is valid.
        userId = await validateSession(sessionId);

        if (!userId) {
            return resolve({ success: false, message: '❌ Error validating session! Login again!' });
        }

        // Step 2: Validate Password
        const validationError = validateMasterPassword(masterPassword);
        if (validationError) {
            return resolve({ success: false, message: `❌ ${validationError}` });
        }

        try {
            const hashed = await bcrypt.hash(masterPassword, 10);
            const db = new sqlite3.Database(dbPath);

            db.run(
                `UPDATE users SET masterPassword = ?, updated_at = ? WHERE id = ?`,
                [hashed, new Date().toISOString(), userId],
                async (err) => {
                    db.close();
                    if (err) {
                        return resolve({ success: false, message: '❌ Failed to save master password.' });
                    }

                    const success = await storeMasterPasswordInSession(sessionId, masterPassword);
                    if (!success) {
                        return resolve({ success: false, message: '❌ Failed to store master password in session.' });
                    }

                    resolve({ success: true, message: '✅ Master password set successfully!' });
                }
            );
        } catch (err) {
            console.error('setMasterPassword Error:', err);
            resolve({ success: false, message: '❌ Unexpected error.' });
        }
    });
}

// Verify master password (data = { userId, masterPassword })
function verifyMasterPassword({ userId, masterPassword }) {
    return new Promise((resolve) => {
        // This should compare the hashed version with DB
        resolve({ success: true, message: '✅ [verifyMasterPassword] Placeholder implementation.' });
    });
}



module.exports = {
    createUser,
    loginUser,
    setMasterPassword,
    verifyMasterPassword
};
