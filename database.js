const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');

// Initialize and connect to the database
const db = new sqlite3.Database('./userdata.db', sqlite3.OPEN_READWRITE | sqlite3.OPEN_CREATE, (err) => {
    if (err) {
        console.error(err.message);
    }
    console.log('Connected to the userdata database.');
    initializeDB();
});

function initializeDB() {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )`);
}

// Function to add a new user
function createUser(username, password, callback) {
    const id = uuidv4(); // Generate a unique UUID for each user
    db.run(`INSERT INTO users (id, username, password) VALUES (?, ?, ?)`, [id, username, password], function (err) {
        callback(err, { id, username });
    });
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
