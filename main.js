const { app, BrowserWindow, Tray, Menu } = require("electron");

/**
 * Bot Management
 */
const {
    loginFacebook,
    interactWithProfile,
    goBackToHome,
    searchPages,
    likePage,
    likeRandomPost,
    watchVideos,
    generateRandomInteraction,
    likeRandomPostFromPage,
    isOnFacebookHome
} = require("./bot/facebookActions");
const { waitRandom, waitMust } = require("./bot/utility");

/**
 * user management
 */
const {
    createUser,
    loginUser,
    setMasterPassword,
    verifyMasterPassword,
    storeFacebookCredentials,
} = require("./database/users");
const {
    initUserTable,
    initSessionTable,
    initKeywordAndPagesTables,
    initVideoTable,
    initSyncConfigTable,
    initPostsTable,
} = require("./database/db");
const {
    validateSession,
    getMasterPasswordFromSession,
    invalidateSession,
    clearSession,
} = require("./database/session");
const { fetchAllKeywords, addKeywords, numberOfKeywords } = require("./database/keywords");
const { saveSyncStatus, fetchSyncStatus, runSyncForUser } = require("./database/sync");
const { getUsageStats } = require("./database/stat");

/**
 * Utility and Others
 */
const { writeLog, readLog, readAllLog } = require("./utility/logmanager");
const puppeteer = require("puppeteer");

const { ipcMain } = require("electron");
const fs = require("fs");
const path = require("path");

require('dotenv').config(); // ⬅️ Load env vars from .env file
const isDev = process.env.NODE_ENV === 'development';

const iconPath = isDev
    ? path.join(__dirname, 'assets', 'MetaPriv-32.png')
    : path.join(process.resourcesPath, 'assets', 'MetaPriv-32.png');


try {
    const axios = require('axios');
} catch (err) {
    console.error("❌ Error loading AXIOS:", err);
}

app.setAboutPanelOptions({}); // To initialize app early

app.on('will-finish-launching', () => {
    app.disableHardwareAcceleration(); // extra safety
});
app.on('ready', () => {
    app.setLoginItemSettings({ openAtLogin: false }); // also forces init
});
app.setAppUserModelId(process.execPath); // for Windows tray bugs too

let browser = null; // Global browser instance
let botProcess = null; // Track Puppeteer page
let tray = null;

// Disable GPU acceleration for Electron
app.commandLine.appendSwitch("disable-gpu");
app.commandLine.appendSwitch("disable-software-rasterizer");
app.commandLine.appendSwitch("disable-features", "VizDisplayCompositor");

// Declare App name
app.setName("MetaPriv");


function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        title: "MetaPriv",
        webPreferences: {
            nodeIntegration: true,
            preload: path.join(__dirname, "preload.js"),
            nodeIntegration: false,
        },
    });

    const indexPath = path.join(__dirname, 'frontend', 'build', 'index.html');
    win.loadURL(`file://${indexPath}`);

    /**
     * database setup | will not create if already exists.
     * this is to ensure that the database is created only once.
     */
    initUserTable(); // Ensure the table exists on app start
    initSessionTable();
    initVideoTable();
    initKeywordAndPagesTables();
    initSyncConfigTable();
    initPostsTable();

    /**
     * TRAAAAy
     */
    // Minimize to tray behavior
    win.on('minimize', (event) => {
        event.preventDefault();
        win.hide();
    });

    // Restore from tray when clicked on Dock (Mac)
    app.on('activate', () => {
        if (win) win.show();
    });

    // ✅ Setup Tray
    tray = new Tray(iconPath);
    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Open MetaPriv',
            click: () => {
                win.show();
            },
        },
        {
            label: 'Close MetaPriv',
            click: () => {
                app.quit();
            },
        },
    ]);
    tray.setToolTip('MetaPriv');
    tray.setContextMenu(contextMenu);

    // ✅ Show on click (optional)
    tray.on('click', () => {
        win.show();
    });
}

async function initBrowser() {
    const userDataPath = path.join(app.getPath('userData'), 'user_data');

    // Ensure the directory exists
    if (!fs.existsSync(userDataPath)) {
        fs.mkdirSync(userDataPath, { recursive: true });
    }
    const isFirstRun = !fs.existsSync(userDataPath);

    if (!browser) {
        browser = await puppeteer.launch({
            headless: false,
            args: [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--force-device-scale-factor=1",
                "--disable-notifications",
                "--disable-gpu",
                "--disable-features=VizDisplayCompositor",
            ],
            userDataDir: userDataPath, // Set the userDataDir to persist session data
        });
    }

    return isFirstRun; // Return whether it's the first run based on the existence of user_data
}

async function testWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        title: "MetaPriv - Test Window",
        webPreferences: {
            nodeIntegration: true,
            preload: path.join(__dirname, "preload.js"),
            nodeIntegration: false,
        },
    });

    initPostsTable();

    try {
        await initBrowser();
        const page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 720 });
        console.log("Browser initialized successfully.");

        await waitMust(5);
        likeRandomPostFromPage(page);

    } catch (error) {
        console.error("Error initializing browser:", error);
        return;
    }
}


app.on('ready', () => {
    app.setAppUserModelId('fi.tuni.asif.ibtehaz'); // good to match build ID
});

app.whenReady().then(createWindow);
// app.whenReady().then(testWindow); // TEST

app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
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

app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

/**
 * Inter Process Communication
 */

ipcMain.handle("run-bot", async (_event, { sessionId }) => {
    if (botProcess) return "⚠️ Bot already running.";
    const userId = await validateSession(sessionId);

    if (!userId) {
        return {
            success: false,
            message: "❌ Invalid session.",
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

        const status = await isOnFacebookHome(page, masterPassword);
        if (!status) {
            writeLog("❌ Not on Facebook Home Page. Aborting bot run.", masterPassword);
            return "❌ Not on Facebook Home Page. Aborting bot run.";
        }

        // await interactWithProfile(page, masterPassword);
        // await waitRandom(20);
        // check here if there are active keywords

        // Linear flow with probability checks
        if (Math.random() <= 0.10) {
            writeLog(`🔍 Running searchPages... Probability 10%`, masterPassword);
            await searchPages(page, userId, masterPassword);
            await waitRandom(30);
        } else {
            writeLog(`🔍 Skipping searchPages...`, masterPassword);
        }

        if (Math.random() <= 0.15) {
            writeLog(`👍 Running likeRandomPostFromPage... Probability 15%`, masterPassword);
            await likeRandomPostFromPage(page, masterPassword);
            await waitRandom(100);
        } else {
            writeLog(`👍 Skipping likeRandomPostFromPage...`, masterPassword);
        }

        if (Math.random() <= 0.05) {
            writeLog(`🌐 Running likePage... Probability 5%`, masterPassword);
            await likePage(page, userId, masterPassword);
            await waitRandom(100);
        } else {
            writeLog(`🌐 Skipping likePage...`, masterPassword);
        }

        if (Math.random() <= 0.70) {
            writeLog(`🎥 Running watchVideos... Probability 70%`, masterPassword);
            await watchVideos(page, userId, masterPassword);
            await waitRandom(200);
        } else {
            writeLog(`🎥 Skipping watchVideos...`, masterPassword);
        }

        // await goBackToHome(page, masterPassword);
        await waitRandom(20);
        await browser.close();

        browser = null;
        writeLog("MetaPriv Finished", masterPassword);
        return "Bot finished";
    } catch (err) {
        console.error(err.stack);
        writeLog(`Run-bot error: ${err}`, masterPassword);
        return "Failed to run bot";
    } finally {
        botProcess = null;
    }
});

ipcMain.on("quit-app", () => {
    if (browser) {
        browser.close().then(() => {
            browser = null;
            app.quit();
        });
    } else {
        app.quit();
    }
});

ipcMain.handle("create-account", async (_event, data) => {
    return await createUser(data);
});

ipcMain.handle("login-account", async (_event, data) => {
    return await loginUser(data);
});

ipcMain.handle("validate-session", async (_event, sessionId) => {
    const userId = await validateSession(sessionId);
    return userId ? { valid: true, userId } : { valid: false };
});

ipcMain.handle("set-master-password", async (_event, data) => {
    return await setMasterPassword(data);
});

ipcMain.handle("verify-master-password", async (_event, data) => {
    return await verifyMasterPassword(data);
});

ipcMain.handle("submit-facebook-auth", async (_event, data) => {
    const { storeFacebookCredentials } = require("./database/users");
    return await storeFacebookCredentials(data);
});

ipcMain.handle("stop-bot", async () => {
    if (botProcess) {
        try {
            await botProcess.close();
            botProcess = null;
            return { success: true, message: "✅ Bot stopped." };
        } catch (err) {
            return { success: false, message: "❌ Failed to stop bot." };
        }
    }
    return { success: false, message: "⚠️ No bot process to stop." };
});

ipcMain.handle("is-bot-running", () => {
    return !!botProcess;
});

ipcMain.handle("fetch-keywords", async (_event, sessionId) => {
    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (masterPassword === null) {
        console.error("masterPassword returned null from the OS. Abort!");
        return {
            success: false,
            message: "❌ Internal/MasterPassword is null!",
            keywords: [],
        };
    }
    try {
        const result = await fetchAllKeywords(sessionId, masterPassword);
        return result; // This will return { success: true/false, message, keywords }
    } catch (error) {
        writeLog(`Error fetching keywords: ${error}`, masterPassword);
        return {
            success: false,
            message: "❌ Failed to fetch keywords due to an internal error.",
            keywords: [],
        };
    }
});

ipcMain.handle("add-keywords", async (_event, { sessionId, keywords }) => {
    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (masterPassword === null) {
        console.error("masterPassword returned null from the OS. Abort!");
        return {
            success: false,
            message: "❌ Internal/MasterPassword is null!",
            keywords: [],
        };
    }
    try {
        const result = await addKeywords(sessionId, keywords, masterPassword);
        return result;
    } catch (error) {
        writeLog(`Error adding keywords: ${error}`, masterPassword);
        return {
            success: false,
            message: "❌ Failed to ADD keywords due to an internal error.",
        };
    }
});

ipcMain.handle("fetch-recent-logs", async (_event, data) => {
    const sessionId = data.sessionId;
    const currentTime = data.currentTime;
    const lastMessage = data.lastMessage;

    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (masterPassword === null) {
        console.error("masterPassword returned null from the OS. Abort!");
        return {
            success: false,
            message: "❌ Internal/MasterPassword is null!",
            logs: [],
        };
    }
    // console.log("currentTime: ", currentTime, " Last Message: ", lastMessage);

    try {
        const logs = await readLog(masterPassword, currentTime, lastMessage);
        return {
            success: true,
            logs: logs,
        };
    } catch (error) {
        writeLog(`Error reading logs: ${error}`, masterPassword);
        return { success: false, message: "❌ Failed to read logs.", logs: [] };
    }
});

ipcMain.handle("activity-logs", async (_event, sessionId) => {
    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (masterPassword === null) {
        console.error("masterPassword returned null from the OS. Abort!");
        return {
            success: false,
            message: "❌ Internal/MasterPassword is null!",
            logs: [],
        };
    }
    try {
        logs = readAllLog(masterPassword);
        return {
            success: true,
            logs: logs,
        };
    } catch (error) {
        writeLog(`Error reading all logs: ${error}`, masterPassword);
        return { success: false, message: "❌ Failed to read all logs.", logs: [] };
    }
});

ipcMain.handle("invalidate-session", async (_event, sessionId) => {
    try {
        await invalidateSession(sessionId);
        await clearSession(sessionId);
        return { success: true, message: "Session invalidated. Logout complete!" };
    } catch (error) {
        console.error("Invalid Session Error occurred : ", error);
        return null;
    }
});

ipcMain.handle('save-sync-settings', async (_event, { sessionId, backendUrl, syncPeriod }) => {
    const userId = await validateSession(sessionId);
    if (!userId) {
        return {
            success: false,
            message: '❌ Invalid session. Please log in again.',
        };
    }

    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (masterPassword === null) {
        console.error("masterPassword returned null from the OS. Abort!");
        return {
            success: false,
            message: "❌ Internal/MasterPassword is null!"
        };
    }

    try {
        // Normalize backend URL to base
        const urlObject = new URL(backendUrl);
        const baseUrl = `${urlObject.protocol}//${urlObject.hostname}${urlObject.port ? `:${urlObject.port}` : ''}/`;

        // Check /status endpoint
        const statusUrl = new URL('/status', baseUrl).href;
        const response = await axios.get(statusUrl);

        if (response.status !== 200) {
            return {
                success: false,
                message: `❌ Backend /status returned status ${response.status}`,
            };
        }

        // Save only baseUrl (clean) to DB
        const result = await saveSyncStatus(userId, baseUrl, syncPeriod);
        if (result.success) {
            return {
                success: true,
                message: '✅ Sync settings saved successfully!',
            };
        } else {
            return {
                success: false,
                message: `❌ Failed to save sync settings! ${result.message}`,
            };
        }
    } catch (error) {
        writeLog(`Error during sync settings save: ${error}`, masterPassword);
        return {
            success: false,
            message: `❌ Error Occurred: ${error.message}`,
        };
    }
});


ipcMain.handle("fetch-sync-status", async (_event, sessionId) => {
    const userId = await validateSession(sessionId);
    if (!userId) {
        return {
            success: false,
            message: '❌ Invalid session. Please log in again.',
        };
    }

    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (masterPassword === null) {
        console.error("masterPassword returned null from the OS. Abort!");
        return {
            success: false,
            message: "❌ Internal/MasterPassword is null!"
        };
    }

    try {
        const result = await fetchSyncStatus(userId);
        if (result.success) {
            return {
                success: true,
                message: '✅ Sync status fetched successfully!',
                data: result,
            };
        } else {
            return {
                success: false,
                message: `❌ Failed to fetch sync status! ${result.message}`,
            };
        }
    } catch (error) {
        writeLog(`Error during sync status fetch: ${error}`, masterPassword);
        return {
            success: false,
            message: `❌ Error Occurred: ${error.message}`,
        };
    }
});


ipcMain.handle('run-manual-sync', async (_event, sessionId) => {
    const userId = await validateSession(sessionId);
    if (!userId) return { success: false, message: 'Invalid session.' };

    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (masterPassword === null) {
        console.error("masterPassword returned null from the OS. Abort!");
        return {
            success: false,
            message: "❌ Internal Error Occurred! Please login again!"
        };
    }

    try {
        // Your manual sync logic here
        return await runSyncForUser(userId, masterPassword);
    } catch (err) {
        console.error('Manual sync error:', err);
        return { success: false, message: err.message };
    }
});


ipcMain.handle('get-usage-stats', async (_event, sessionId) => {
    try {
        const stats = await getUsageStats(sessionId);
        return { success: true, stats };
    } catch (error) {
        console.error('❌ Failed to get usage stats:', error.message);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('count-keywords', async (_event, sessionId) => {
    const userId = await validateSession(sessionId);
    if (!userId) {
        return {
            success: false,
            message: '❌ Invalid session. Please log in again.',
        };
    }

    const masterPassword = await getMasterPasswordFromSession(sessionId);
    if (masterPassword === null) {
        console.error("masterPassword returned null from the OS. Abort!");
        return {
            success: false,
            message: "❌ Internal/MasterPassword is null!",
        };
    }
    try {
        const result = await numberOfKeywords(userId);
        return result; // This will return { success: true/false, message, count }
    } catch (error) {
        writeLog(`Error counting keywords: ${error}`, masterPassword);
        return {
            success: false,
            message: "❌ Failed to count keywords due to an internal error.",
        };
    }
}
);
