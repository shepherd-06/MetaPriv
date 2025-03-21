const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');
const moment = require('moment');

// Initialize and connect to the database
const db = new sqlite3.Database('./userdata.db', sqlite3.OPEN_READWRITE | sqlite3.OPEN_CREATE, (err) => {
    if (err) {
        console.error(err.message);
    }
    console.log('Connected to the userdata database.');
    initializeDB();
});

function initializeDB() {
    db.run(`
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            masterPassword TEXT,
            createdOn DATETIME NOT NULL,
            lastSeenOn DATETIME
        )
    `, function (err) {
        if (err) {
            console.error('Error when creating the users table', err);
        } else {
            console.log('Users table created or already exists.');
        }
    });
}

// Function to add a new user
function createUser(username, hashedPassword, callback) {
    const id = uuidv4(); // Generate a unique UUID for each user
    const createdOn = datetime('now'); // Get the current date and time in SQL compatible format
    const lastSeenOn = createdOn; // Initially set the last seen to the created date

    db.run(`INSERT INTO users (id, username, password, masterPassword, createdOn, lastSeenOn) VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))`,
        [id, username, hashedPassword, null],
        function (err) {
            if (err) {
                return callback(err);
            }
            callback(null, { id, username, createdOn: this.createdOn, lastSeenOn: this.lastSeenOn });
        }
    );

}

// Function to find a user by username
function findUserByUsername(username, callback) {
    db.get(`SELECT * FROM users WHERE username = ?`, [username], (err, row) => {
        callback(err, row);
    });
}

// Close the database when the application exits
function closeDB() {
    db.close((err) => {
        if (err) {
            return console.error(err.message);
        }
        console.log('Closed the database connection.');
    });
}

module.exports = { createUser, findUserByUsername, closeDB };
