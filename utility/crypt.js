const crypto = require('crypto');

function aesEncrypt(text, masterKey) {
    if (Buffer.from(masterKey).length !== 24) {
        throw new Error('Master key must be exactly 24 bytes (192 bits) for AES-192.');
    }
    const cipher = crypto.createCipheriv('aes-192-cbc', Buffer.from(masterKey), Buffer.alloc(16, 0));
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return encrypted;
}


function aesDecrypt(encryptedText, masterKey) {
    if (Buffer.from(masterKey).length !== 24) {
        throw new Error('Master key must be exactly 24 bytes (192 bits) for AES-192.');
    }
    const decipher = crypto.createDecipheriv('aes-192-cbc', Buffer.from(masterKey), Buffer.alloc(16, 0));
    let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
}


module.exports = {
    aesEncrypt,
    aesDecrypt
}