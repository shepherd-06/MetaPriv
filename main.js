const { app, BrowserWindow } = require('electron');

/**
 * Bot Management
 */
const { loginFacebook, interactWithProfile,
    goBackToHome, searchPages, likePage,
    likeRandomPost, watchVideos, generateRandomInteraction } = require('./bot/facebookActions');
const { waitRandom, waitMust } = require('./bot/utility');

/**
 * user management
 */
const { createUser, loginUser,
    setMasterPassword, verifyMasterPassword, storeFacebookCredentials, } = require('./database/users');
const { initUserTable, initSessionTable,
    initKeywordAndPagesTables, initVideoTable } = require('./database/db');
const { validateSession, getMasterPasswordFromSession } = require('./database/session');
const { fetchAllKeywords, addKeywords } = require('./database/keywords');

/**
 * Utility and Others
 */
const { writeLog } = require('./utility/logmanager');
const puppeteer = require('puppeteer');
const { ipcMain } = require('electron');
const fs = require('fs');
const path = require('path');


let browser = null;  // Global browser instance
let botProcess = null; // Track Puppeteer page

// Disable GPU acceleration for Electron
app.commandLine.appendSwitch('disable-gpu');
app.commandLine.appendSwitch('disable-software-rasterizer');
app.commandLine.appendSwitch('disable-features', 'VizDisplayCompositor');


function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false
        }
    });

    // win.loadFile(path.join(__dirname, 'frontend/build/index.html'));
    win.loadURL('http://localhost:3000'); // React dev server in dev mode.

    /**
     * database setup | will not create if already exists.
     * this is to ensure that the database is created only once.
     */
    initUserTable(); // Ensure the table exists on app start
    initSessionTable();
    initVideoTable();
    initKeywordAndPagesTables();
}

async function initBrowser() {
    const userDataPath = path.join(__dirname, 'user_data');
    const isFirstRun = !fs.existsSync(userDataPath);

    if (!browser) {
        browser = await puppeteer.launch({
            headless: false,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--force-device-scale-factor=1',
                '--disable-notifications',
                '--disable-gpu',
                '--disable-features=VizDisplayCompositor',
            ],
            userDataDir: userDataPath // Set the userDataDir to persist session data
        });
    }

    return isFirstRun;  // Return whether it's the first run based on the existence of user_data
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        if (browser) {
            browser.close().then(() => {
                browser = null;
                app.quit();
            });
        } else {
            app.quit();
        }
    }
});


app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

/**
 * Inter Process Communication
 */

ipcMain.handle('run-bot', async (_event, { sessionId }) => {
    if (botProcess) return '⚠️ Bot already running.';
    const userId = await validateSession(sessionId);

    if (!userId) {
        return {
            success: false,
            message: '❌ Invalid session.',
        };
    }

    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (masterPassword === null) {
        console.error("masterPassword returned null from the OS. Abort!");
        return "❌ Internal/MasterPassword is null!";
    }

    try {
        await initBrowser();
        const page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 720 });
        botProcess = browser;
        writeLog("MetaPriv Starting....", masterPassword);

        try {
            // we will try to login always. 
            // if login form exist it will login.
            // or else it will crash and load the facebook page. 
            await loginFacebook(page, sessionId, masterPassword);
            await waitRandom(5);
        } catch (err) {
            writeLog(`User is probably logged in. || error: ${err}`, masterPassword);
            // If login fails, we can still proceed to the main page
            await page.goto("https://facebook.com");
            await waitMust(10);
        }
        await goBackToHome(page, masterPassword);
        await waitRandom(20);
        await searchPages(page, userId, masterPassword);
        // await waitRandom(30);
        await likePage(page, userId, masterPassword);
        // await waitRandom(30);

        await likeRandomPost(page, masterPassword);
        // await waitRandom(20);

        await watchVideos(page, userId, masterPassword);
        // await waitRandom(20);

        await goBackToHome(page, masterPassword);
        await waitRandom(20);
        await browser.close();

        browser = null;
        writeLog("MetaPriv Finished", masterPassword);
        return 'Bot finished';
    } catch (err) {
        writeLog(`Run-bot error: ${err}`, masterPassword);
        return 'Failed to run bot';
    } finally {
        botProcess = null;
    }
});

ipcMain.on('quit-app', () => {
    if (browser) {
        browser.close().then(() => {
            browser = null;
            app.quit();
        });
    } else {
        app.quit();
    }
});

ipcMain.handle('create-account', async (_event, data) => {
    return await createUser(data);
});

ipcMain.handle('login-account', async (_event, data) => {
    return await loginUser(data);
});

ipcMain.handle('validate-session', async (_event, sessionId) => {
    const userId = await validateSession(sessionId);
    return userId ? { valid: true, userId } : { valid: false };
});

ipcMain.handle('set-master-password', async (_event, data) => {
    return await setMasterPassword(data);
});

ipcMain.handle('verify-master-password', async (_event, data) => {
    return await verifyMasterPassword(data);
});

ipcMain.handle('submit-facebook-auth', async (_event, data) => {
    const { storeFacebookCredentials } = require('./database/users');
    return await storeFacebookCredentials(data);
});

ipcMain.handle('stop-bot', async () => {
    if (botProcess) {
        try {
            await botProcess.close();
            botProcess = null;
            return { success: true, message: '✅ Bot stopped.' };
        } catch (err) {
            return { success: false, message: '❌ Failed to stop bot.' };
        }
    }
    return { success: false, message: '⚠️ No bot process to stop.' };
});

ipcMain.handle('is-bot-running', () => {
    return !!botProcess;
});

ipcMain.handle('fetch-keywords', async (_event, sessionId) => {
    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (masterPassword === null) {
        console.error("masterPassword returned null from the OS. Abort!");
        return { success: false, message: '❌ Internal/MasterPassword is null!', keywords: [] };
    }
    try {
        const result = await fetchAllKeywords(sessionId);
        return result; // This will return { success: true/false, message, keywords }
    } catch (error) {
        writeLog(`Error fetching keywords: ${error}`, masterPassword);
        return { success: false, message: '❌ Failed to fetch keywords due to an internal error.', keywords: [] };
    }
});

ipcMain.handle('add-keywords', async (_event, { sessionId, keywords }) => {
    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (masterPassword === null) {
        console.error("masterPassword returned null from the OS. Abort!");
        return { success: false, message: '❌ Internal/MasterPassword is null!', keywords: [] };
    }
    try {
        const result = await addKeywords(sessionId, keywords);
        return result;
    } catch (error) {
        writeLog(`Error adding keywords: ${error}`, masterPassword);
        return { success: false, message: '❌ Failed to ADD keywords due to an internal error.' };
    }
});