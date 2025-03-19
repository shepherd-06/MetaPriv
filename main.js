const { app, BrowserWindow } = require('electron');
const { exec } = require('child_process');
const waitOn = require('wait-on');

app.whenReady().then(async () => {
    const mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true
        }
    });

    console.log("🚀 Starting Flask server...");
    const flaskProcess = exec("python3 app.py");

    await waitOn({ resources: ['http://127.0.0.1:5555'], timeout: 20000 })
        .then(() => {
            console.log("✅ Flask server is running. Opening Electron App...");
            mainWindow.loadURL('http://127.0.0.1:5555');
        })
        .catch(err => {
            console.error("❌ Flask did not start in time:", err);
            mainWindow.loadURL("data:text/html,Flask server failed to start. Try restarting.");
        });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        app.whenReady().then(async () => createWindow());
    }
});
