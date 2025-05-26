const fs = require('fs');
const readline = require('readline');
const path = require('path');
const os = require('os');
const { aesEncrypt, aesDecrypt } = require('./crypt');
const { app } = require('electron');

// Get the user-writable directory provided by Electron
const logDir = path.join(app.getPath('userData'), 'logs');

// Ensure the directory exists
if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
}

// Define the log file path
const logFile = path.join(logDir, 'bot_logs.log');

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

/**
 * Read, decrypt, and return recent logs based on time and last received message.
 *
 * What it does:
 * - Reads the log file line by line (memory efficient for big files).
 * - Decrypts each line (if decryption fails, keeps the original encrypted text with a "Failed to decrypt" prefix).
 * - If a line has no timestamp, it's treated as part of the previous log entry (multi-line logs).
 * - Only processes logs within the last 7 seconds (+ 2 seconds padding) compared to `currentTime`.
 * - Stops reading early once older logs are hit (based on the last timestamped log).
 * - Returns logs *after* the last received `lastMessage`.
 *
 * @param {string} key - The encryption key for decryption.
 * @param {string} currentTime - The current time in ISO string format (from the front-end).
 * @param {string} lastMessage - The last log message the front-end received (empty string if none yet).
 * @returns {Promise<string[]>} A promise that resolves to an array of new log lines.
 */
async function readLog(key, currentTime, lastMessage) {
    if (!fs.existsSync(logFile)) return [];

    const now = new Date(currentTime);
    if (isNaN(now.getTime())) {
        console.error('Invalid currentTime format.');
        return [];
    }

    const resultLogs = [];
    let bufferLog = ''; // To hold multi-line logs
    let lastTimestamp = null;
    let foundLastMessage = lastMessage === ''; // if empty, start collecting immediately

    const rl = readline.createInterface({
        input: fs.createReadStream(logFile),
        crlfDelay: Infinity
    });

    for await (const line of rl) {
        if (!line.trim()) continue; // skip empty lines

        let decryptedLine;
        try {
            decryptedLine = aesDecrypt(line, key);
        } catch (e) {
            decryptedLine = `Failed to decrypt - ${line}`;
        }

        const match = decryptedLine.match(/^\[(.*?)\]/); // Check if this line has a timestamp
        if (match) {
            // This is a new log entry (timestamped)
            // console.log("Match found : ", match);
            // multi-line log before, handle it first
            if (bufferLog) {
                // the previous buffered log
                const prevMatch = bufferLog.match(/^\[(.*?)\]/);
                if (prevMatch) {
                    const logTimeStr = prevMatch[1];
                    const logTime = new Date(logTimeStr.replace(' ', 'T'));

                    const diffInSeconds = (now - logTime) / 1000;

                    if (diffInSeconds >= -2 && diffInSeconds <= 7) {
                        if (foundLastMessage) {
                            resultLogs.push(bufferLog);
                        } else if (bufferLog === lastMessage) {
                            foundLastMessage = true;
                        }
                    }

                    // Early exit if the log is too old
                    if (diffInSeconds > 9) {
                        rl.close();
                        break;
                    }
                }
            }

            // Start a new buffer with this new log entry
            bufferLog = decryptedLine;
            lastTimestamp = match[1]; // Update current timestamp
            // console.log("Start a new buffer with this new log entry ", bufferLog);
            // console.log("lastTimestamp: ", lastTimestamp);

        } else {
            // Continuation of the previous log entry
            if (bufferLog) {
                bufferLog += '\n' + decryptedLine;
                // console.log("Continuation of the previous log entry ", bufferLog);
            } else {
                // Very rare case: continuation without any previous log
                bufferLog = decryptedLine;
                // console.log("very rare case: ", bufferLog);
            }
        }
    }

    // last buffered log after the loop ends
    if (bufferLog) {
        const finalMatch = bufferLog.match(/^\[(.*?)\]/);
        if (finalMatch) {
            const logTimeStr = finalMatch[1];
            const logTime = new Date(logTimeStr.replace(' ', 'T'));

            const diffInSeconds = (now - logTime) / 1000;

            if (diffInSeconds >= -2 && diffInSeconds <= 7) {
                if (foundLastMessage) {
                    resultLogs.push(bufferLog);
                } else if (bufferLog === lastMessage) {
                    // Edge case: last log IS the lastMessage, no new logs
                }
            }
        }
    }

    return resultLogs;
}


module.exports = {
    writeLog,
    readLog,
    readAllLog,
};
