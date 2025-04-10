const { app, BrowserWindow } = require('electron');
require('dotenv').config();
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');


let browser = null;  // Global browser instance

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


function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true
        }
    });

    win.loadFile('web/index.html');
    initBrowser().then(async (isFirstRun) => {
        const page = await browser.newPage(); // Create a new page here and use it in both functions
        await page.setViewport({ width: 1280, height: 720 });

        if (isFirstRun) {
            await loginFacebook(page);  // Only perform login on first run
        }
        await waitRandom(5); // wait between 1 to 5 seconds on random.
        await interactWithProfile(page); // go to profile and scroll a little bit.
    }).catch(console.error);
}

// async function initBrowser() {
//     if (!browser) {
//         browser = await puppeteer.launch({
//             headless: false, // Set headless to false for visual debugging
//             args: ['--no-sandbox',
//                 '--disable-setuid-sandbox',
//                 '--force-device-scale-factor=1',
//                 '--disable-notifications']
//         });
//     }
// }

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
                '--disable-notifications'
            ],
            userDataDir: userDataPath // Set the userDataDir to persist session data
        });
    }

    return isFirstRun;  // Return whether it's the first run based on the existence of user_data
}


async function waitRandom(randomLimit) {
    // Generate a random number of milliseconds between 1000 (1 second) and randomLimit seconds
    const waitTime = Math.random() * (randomLimit * 1000 - 1000) + 1000;
    console.log("wait - time ", waitTime, " ms");
    // Wait for the calculated random time
    await new Promise(resolve => setTimeout(resolve, waitTime));
}

async function waitMust(timeS) {
    // must wait the time seconds
    await new Promise(resolve => setTimeout(resolve, timeS * 1000));
}

async function loginFacebook(page) {
    try {
        await page.goto('https://www.facebook.com');
        await waitRandom(10);

        const cookieButtonSelector = 'div[role="none"].x1ja2u2z.x78zum5.x2lah0s.x1n2onr6.xl56j7k.x6s0dn4.xozqiw3.x1q0g3np.xi112ho.x17zwfj4.x585lrc.x1403ito.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xn6708d.x1ye3gou.xtvsq51.x1r1pt67 div[role="none"] span[dir="auto"]';
        await page.click(cookieButtonSelector);

        // caution TODO: replace TO OS based password retrieval.
        const test_email = process.env.TEST_FB_EMAIL;
        const test_pass = process.env.TEST_FB_PASS;

        await new Promise(resolve => setTimeout(resolve, 1000));
        await page.type('#email', test_email, { delay: 30 });
        await waitRandom(10);
        await page.type('#pass', test_pass, { delay: 30 });
        await waitRandom(10);
        await page.click('button[name="login"]');

        // at least 10 seconds waiting.
        await waitMust(20);
        // Commented out to prevent automatic navigation wait
        console.log('Logged in or still on login page for debugging.');
    } catch (error) {
        console.error('An error occurred:', error);
    }
}

async function interactWithProfile(page) {
    /**
     * After Facebook has been loaded, go to profile, scroll a little bit for no apparent reason,
     * go back to home page.
     */
    try {
        await page.goto('https://www.facebook.com');
        await waitMust(10);
        console.log("Interacting with profile");
        const profileSelector = 'a[aria-label*="Timeline"]'; // This selector targets a link to a user's timeline, assuming 'Timeline' is part of the aria-label
        await page.click(profileSelector);
        // Wait a random amount of time between 1 to 20 seconds, then scroll
        await waitRandom(20);
        await page.evaluate(() => window.scrollBy(0, 500)); // Scroll down 500 pixels
        await waitMust(10); // Wait 10 seconds

        // Navigate back to the homepage
        await goBackToHome(page);
        console.log('Profile interaction completed');
    } catch (error) {
        console.error('An error occurred:', error);
    }
}

async function goBackToHome(page) {
    /**
     * function to go back home when needed.
     */
    try {
        console.log("Attempting to click the Facebook logo...");
        const logoSelector = 'a[aria-label="Facebook"]';
        await page.click(logoSelector);
        console.log("Facebook logo clicked successfully.");
        await waitMust(10); // Wait 10 seconds
    } catch (error) {
        console.error('An error occurred while trying to click the Facebook logo:', error);
    }
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
