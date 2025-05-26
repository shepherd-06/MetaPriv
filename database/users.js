const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const { app } = require('electron');
const fs = require('fs');

const dbDir = app.getPath('userData');
const dbPath = path.join(dbDir, 'users.db');

// Ensure the directory exists (just in case)
if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
}

/**
 * session management
 */
const { createSession, storeMasterPasswordInSession, validateSession } = require('./session');

/** 
 * FB Auth
*/
const keytar = require('keytar');
const { getMasterPasswordFromSession } = require('./session');
const { aesEncrypt, aesDecrypt } = require('../utility/crypt');
const SERVICE_NAME = 'MetaPriv.FBAuth';

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

                    const success = await storeMasterPasswordInSession(userId, masterPassword);
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

// Verify master password (data = { sessionId, masterPassword })
function verifyMasterPassword({ sessionId, masterPassword }) {
    return new Promise(async (resolve) => {
        try {
            // Step 1: Validate session and get userId
            const userId = await validateSession(sessionId);
            if (!userId) {
                return resolve({ success: false, message: '❌ Invalid or expired session.' });
            }

            // Step 2: Get hashed master password from DB
            const db = new sqlite3.Database(dbPath);
            db.get(
                `SELECT masterPassword, fbEmail FROM users WHERE id = ?`,
                [userId],
                async (err, row) => {
                    db.close();

                    if (err || !row || !row.masterPassword) {
                        return resolve({ success: false, message: '❌ Master password not set or DB error.' });
                    }

                    const match = await bcrypt.compare(masterPassword, row.masterPassword);
                    const onboardingStep = row.fbEmail && row.fbEmail.trim() !== '' ? 5 : 4;
                    if (match) {
                        const state = await storeMasterPasswordInSession(userId, masterPassword);
                        console.info("master password updated in keyTar ", state);
                        console.info("onboarding step ", onboardingStep);
                        return resolve({ success: true, message: '✅ Master password verified.', onboardingStep: onboardingStep });
                    } else {
                        return resolve({ success: false, message: '❌ Incorrect master password.' });
                    }
                }
            );
        } catch (error) {
            console.error('Error verifying master password:', error);
            resolve({ success: false, message: '❌ Unexpected error during verification.' });
        }
    });
}


// Set FB Auth
async function storeFacebookCredentials({ sessionId, fbEmail, fbPassword }) {
    const userId = await validateSession(sessionId);
    if (!userId) {
        return { success: false, message: 'Session expired or invalid.' };
    }

    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (!masterPassword) {
        return { success: false, message: 'Master password not found in session.' };
    }

    // Encrypt email using master password
    const encryptedEmail = aesEncrypt(fbEmail, masterPassword);

    // Store encrypted email in DB
    return new Promise((resolve) => {
        const db = new sqlite3.Database(dbPath);
        const updatedAt = new Date().toISOString();
        db.run(
            `UPDATE users SET fbEmail = ?, updated_at = ? WHERE id = ?`,
            [encryptedEmail, updatedAt, userId],
            async (err) => {
                db.close();

                if (err) {
                    return resolve({ success: false, message: 'Database error.' });
                }

                // Store in system keychain
                try {
                    await keytar.setPassword(SERVICE_NAME, fbEmail, fbPassword);
                    resolve({ success: true, message: '✅ Facebook credentials securely stored.' });
                } catch (e) {
                    resolve({ success: false, message: '❌ Failed to store password in keychain.' });
                }
            }
        );
    });
}

async function getFacebookCredentials(sessionId) {
    const userId = await validateSession(sessionId);
    if (!userId) {
        return { success: false, message: 'Session expired or invalid.' };
    }

    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (!masterPassword) {
        return { success: false, message: 'Master password not found in session.' };
    }

    return new Promise((resolve) => {
        const db = new sqlite3.Database(dbPath);

        db.get(`SELECT fbEmail FROM users WHERE id = ?`, [userId], async (err, row) => {
            db.close();

            if (err || !row || !row.fbEmail) {
                return resolve({ success: false, message: '❌ Could not fetch encrypted email.' });
            }

            try {
                const decryptedEmail = aesDecrypt(row.fbEmail, masterPassword);
                const storedPassword = await keytar.getPassword(SERVICE_NAME, decryptedEmail);

                if (!storedPassword) {
                    return resolve({ success: false, message: '❌ Password not found in keyring.' });
                }

                return resolve({
                    success: true,
                    email: decryptedEmail,
                    password: storedPassword
                });
            } catch (error) {
                console.error("Failed to decrypt or fetch credentials:", error);
                return resolve({ success: false, message: '❌ Decryption or keytar error.' });
            }
        });
    });
}



module.exports = {
    createUser,
    loginUser,
    setMasterPassword,
    verifyMasterPassword,
    storeFacebookCredentials,
    getFacebookCredentials,
};
