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


function initVideoTable() {
  const db = new sqlite3.Database(dbPath);

  const createTableSQL = `
      CREATE TABLE IF NOT EXISTS videos (
          id TEXT PRIMARY KEY,
          post_URL TEXT,
          page_URL TEXT,
          keyword TEXT,
          userId TEXT,
          liked INTEGER,
          time TEXT,
          screenshot_name TEXT,
          watched_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
  `;

  db.run(createTableSQL, (err) => {
    if (err) {
      console.error(`❌ Error creating 'videos' table:`, err.message);
    } else {
      console.log(`✅ 'videos' table with UUID primary key is ready.`);
    }
    db.close();
  });
}

function initKeywordAndPagesTables() {
  const db = new sqlite3.Database(dbPath);

  const createKeywordsTable = `
        CREATE TABLE IF NOT EXISTS keywords (
            id TEXT PRIMARY KEY,
            userId TEXT NOT NULL,
            text TEXT NOT NULL,
            createdAt TEXT NOT NULL,
            isActive INTEGER DEFAULT 1
        );
    `;

  const createPagesTable = `
        CREATE TABLE IF NOT EXISTS pages (
            id TEXT PRIMARY KEY,
            keywordId TEXT NOT NULL,
            pageUrl TEXT NOT NULL,
            isLiked INTEGER DEFAULT 0,
            createdAt TEXT NOT NULL,
            updatedAt TEXT
        );
    `;

  db.serialize(() => {
    db.run(createKeywordsTable, (err) => {
      if (err) {
        console.error("❌ Failed to create 'keywords' table:", err.message);
      } else {
        console.log("✅ 'keywords' table created.");
      }
    });

    db.run(createPagesTable, (err) => {
      if (err) {
        console.error("❌ Failed to create 'pages' table:", err.message);
      } else {
        console.log("✅ 'pages' table created.");
      }
    });

    db.close();
  });
}

module.exports = {
  initUserTable,
  initSessionTable,
  initVideoTable,
  initKeywordAndPagesTables,
};