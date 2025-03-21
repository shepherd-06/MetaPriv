const { app, BrowserWindow, ipcMain } = require('electron');
const { exec } = require('child_process');
const waitOn = require('wait-on');
const path = require('path');


app.whenReady().then(async () => {
    // Main Chat Window
    mainWindow = new BrowserWindow({
        width: 1000,
        height: 700,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
        }
    })

    // Start Flask in the background
    console.log("🚀 Starting Flask server...")
    const flaskProcess = exec("python3 app.py")

    // Wait for Flask to be ready before opening Electron
    await waitOn({ resources: ['http://127.0.0.1:5555'], timeout: 20000 })
        .then(() => {
            console.log("✅ Flask server is running. Opening Electron App...")
            mainWindow.loadURL('http://127.0.0.1:5555')
        })
        .catch(err => {
            console.error("❌ Flask did not start in time:", err)
            mainWindow.loadURL("data:text/html,Flask server failed to start. Try restarting.")
        })
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});