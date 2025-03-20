const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const api = require('./api');

let mainWindow;

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
                reject(err);
            } else {
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
                reject(err);
            } else {
                resolve(user);
            }
        });
    });
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
