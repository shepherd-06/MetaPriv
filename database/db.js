const path = require('path');
const sqlite3 = require('sqlite3').verbose();
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

module.exports = {
    initUserTable,
    initSessionTable,
};