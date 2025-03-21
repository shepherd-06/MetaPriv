const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const api = require('./api');
const keytar = require('keytar');

let mainWindow;

// global variable. temporary session management
global.userInfo = null;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    mainWindow.loadFile('web/index.html');
    mainWindow.on('closed', () => mainWindow = null);
}

app.whenReady().then(createWindow);

// Handle create account request
ipcMain.handle('create-account', async (event, { username, password }) => {
    return new Promise((resolve, reject) => {
        api.createAccount(username, password, (err, user) => {
            if (err) {
                console.error(err)
                reject(err);
            } else {
                console.info("new user created");
                console.info(user)
                global.userInfo = user;
                resolve(user);
            }
        });
    });
});

// Handle login request
ipcMain.handle('login', async (event, { username, password }) => {
    return new Promise((resolve, reject) => {
        api.login(username, password, (err, user) => {
            if (err) {
                console.error(err)
                reject(err);
            } else {
                console.info("login successful");
                global.userInfo = user;
                resolve(user);
            }
        });
    });
});

ipcMain.handle('save-credentials', async (event, { username, password }) => {
    await keytar.setPassword('MetaPriv', username, password);
});

ipcMain.handle('get-credentials', async (event, username) => {
    return await keytar.getPassword('MetaPriv', username);
});

ipcMain.handle('logout', async (event) => {
    // Logic to handle logout
});


app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

function openSetMasterPasswordWindow() {
    let masterPasswordWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    masterPasswordWindow.loadFile('setMasterPassword.html');

    masterPasswordWindow.on('closed', () => {
        masterPasswordWindow = null;
    });
}

// Listen for an IPC message to start the Flask server
// ipcMain.on('start-flask-server', (event, arg) => {
//     console.log("🚀 Starting Flask server...");
//     flaskProcess = exec("python3 app.py");

//     waitOn({ resources: ['http://127.0.0.1:5555'], timeout: 20000 })
//         .then(() => {
//             console.log("✅ Flask server is running. Opening Flask App...");
//             mainWindow.loadURL('http://127.0.0.1:5555');
//         })
//         .catch(err => {
//             console.error("❌ Flask did not start in time:", err);
//             mainWindow.loadURL("data:text/html,Flask server failed to start. Try restarting.");
//         });
// });