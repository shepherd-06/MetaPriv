const { app, BrowserWindow } = require('electron');
const { loginFacebook, interactWithProfile,
    goBackToHome, searchPages, likePage,
    likeRandomPost, watchVideos, generateRandomInteraction } = require('./bot/facebookActions');
const { waitRandom, waitMust } = require('./bot/utility');

/**
 * user management
 */
const { createUser, loginUser,
    setMasterPassword, verifyMasterPassword, storeFacebookCredentials } = require('./database/users');
const { initUserTable, initSessionTable } = require('./database/db');
const { validateSession } = require('./database/session');

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


let urls = [
    "www.facebook.com/friends", // friend list
    "www.facebook.com/watch", // videos
    // suggested bookmarks and stuff
    "https://www.facebook.com/pages/?category=top&ref=bookmarks",
    // recent feed
    "https://www.facebook.com/?sk=h_chr",
    // standard feed
    "https://www.facebook.com/"
]

const dummyPageUrl = [
    'https://www.facebook.com/detectivepikachumovie?__tn__=%3C',
    'https://www.facebook.com/PikachuPratt?__tn__=%3C',
    'https://www.facebook.com/PikachuPikaPi?__tn__=%3C',
    'https://www.facebook.com/IconFighter?__tn__=%3C',
    'https://www.facebook.com/originalhipsterpikachu?__tn__=%3C',
    'https://www.facebook.com/PikachuRidy?__tn__=%3C',
    'https://www.facebook.com/theodorepikachutwicetheyorkielove?__tn__=%3C',
    'https://www.facebook.com/PikachuYT0?__tn__=%3C',
    'https://www.facebook.com/PikachuBunny?__tn__=%3C',
    'https://www.facebook.com/Albinnnn?__tn__=%3C',
    'https://www.facebook.com/Kimotom75?__tn__=%3C'
]


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
     * database setup
     */
    initUserTable(); // Ensure the table exists on app start
    initSessionTable();
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

    try {
        await initBrowser();
        const page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 720 });
        botProcess = browser;

        try {
            // we will try to login always. 
            // if login form exist it will login.
            // or else it will crash and load the facebook page. 
            await loginFacebook(page, sessionId);
            await waitRandom(5);
        } catch (err) {
            console.error('User is probably logged in. || error: ', err);
            // If login fails, we can still proceed to the main page
            await page.goto("https://facebook.com");
            await waitMust(10);
        }

        // await generateRandomInteraction(page);
        await waitRandom(10);
        await goBackToHome(page);

        await waitRandom(20);
        await browser.close();

        browser = null;
        app.relaunch();
        app.exit(0);
        return 'Bot finished';
    } catch (err) {
        console.error('Run-bot error:', err);
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