const fs = require('fs');
const path = require('path');
const os = require('os');
const { aesEncrypt, aesDecrypt } = require('./crypt');


const logDir = path.join(__dirname, '..', 'logs');
const logFile = path.join(logDir, 'bot_logs.log');

// Ensure log folder exists
if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir);
}

/**
 * Write an encrypted log entry with timestamp.
 * Latest logs go to the top of the file.
 */
function writeLog(text, key) {
    const timestamp = new Date().toISOString().replace('T', ' ').split('.')[0];
    const formatted = `[${timestamp}] ${text}`;
    const encrypted = aesEncrypt(formatted, key);

    try {
        const existing = fs.existsSync(logFile) ? fs.readFileSync(logFile, 'utf-8') : '';
        const updated = encrypted + os.EOL + existing;
        fs.writeFileSync(logFile, updated, 'utf-8');
        console.log(formatted); // also print it live
    } catch (err) {
        console.error('Failed to write log:', err);
    }
}

/**
 * Read and decrypt the last N log entries (default 50).
 * Returns an array of log lines.
 */
function readLog(key, limit = 50) {
    try {
        if (!fs.existsSync(logFile)) return [];

        const lines = fs.readFileSync(logFile, 'utf-8')
            .split(/\r?\n/)
            .filter(line => line.trim() !== '')
            .slice(0, limit); // read top N lines (newest entries)

        const decryptedLines = lines.map(line => {
            try {
                return aesDecrypt(line, key);
            } catch (e) {
                return '[Failed to decrypt log entry]';
            }
        });

        return decryptedLines;
    } catch (err) {
        console.error('Failed to read log:', err);
        return [];
    }
}


function readAllLog(key) {
    const result = [];
    try {
        if (!fs.existsSync(logFile)) return result;

        const lines = fs.readFileSync(logFile, 'utf-8')
            .split(/\r?\n/)
            .filter(line => line.trim() !== '');

        lines.forEach(line => {
            try {
                const decrypted = aesDecrypt(line, key);
                result.push(decrypted);
            } catch (e) {
                result.push(`Failed to decrypt - ${line}`);
            }
        });

    } catch (err) {
        console.error('Failed to read log:', err);
    }
    return result;
}

module.exports = {
    writeLog,
    readLog,
    readAllLog,
};
