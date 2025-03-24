const { app, BrowserWindow, ipcMain } = require('electron');
const { exec } = require('child_process');
const waitOn = require('wait-on');
const path = require('path');

let mainWindow;
let flaskProcess = null;

app.disableHardwareAcceleration();

app.whenReady().then(async () => {
    // Create the main window with security preferences
    mainWindow = new BrowserWindow({
        width: 1000,
        height: 700,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false,  // Ensure remote module is disabled
            preload: path.join(__dirname, 'preload.js')  // Use a preload script if needed
        }
    });

    // Start Flask in the background and handle its output
    console.log("🚀 Starting Flask server...");
    flaskProcess = exec("python3 app.py", (error, stdout, stderr) => {
        if (error) {
            console.error(`Exec error: ${error}`);
            return;
        }
        console.log(`Stdout: ${stdout}`);
        console.error(`Stderr: ${stderr}`);
    });

    flaskProcess.stdout.on('data', (data) => {
        console.log('Flask Output: ' + data);
    });

    // Wait for Flask to be ready before opening Electron
    await waitOn({ resources: ['http://127.0.0.1:5555'], timeout: 20000 })
        .then(() => {
            console.log("✅ Flask server is running. Opening Electron App...");
            mainWindow.loadURL('http://127.0.0.1:5555');
        })
        .catch(err => {
            console.error("❌ Flask did not start in time:", err);
            mainWindow.loadURL("data:text/html,<h1>Flask server failed to start. Please restart the application.</h1>");
        });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
});

app.on('window-all-closed', () => {
    // Kill Flask process when all windows are closed
    if (flaskProcess) {
        console.log("Shutting down Flask server...");
        flaskProcess.kill('SIGINT');  // Use SIGINT so Flask can clean up properly
        flaskProcess = null;
    }
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
