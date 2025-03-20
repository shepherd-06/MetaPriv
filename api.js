const bcrypt = require('bcryptjs');
const db = require('./database.js');

function createAccount(username, password, callback) {
    bcrypt.hash(password, 10, (err, hash) => {
        if (err) {
            return callback(err);
        }
        db.createUser(username, hash, callback);
    });
}

function login(username, password, callback) {
    db.findUserByUsername(username, (err, user) => {
        if (err) {
            return callback(err);
        }
        if (user) {
            bcrypt.compare(password, user.password, (err, result) => {
                if (result) {
                    callback(null, user);
                } else {
                    callback(new Error('Invalid credentials'));
                }
            });
        } else {
            callback(new Error('User not found'));
        }
    });
}

module.exports = { createAccount, login };
