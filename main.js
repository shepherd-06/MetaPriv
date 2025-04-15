const { app, BrowserWindow } = require('electron');
const { loginFacebook, interactWithProfile,
    goBackToHome, searchPages, likePage,
    likeRandomPost, watchVideos } = require('./bot/facebookActions');
const { waitRandom, waitMust } = require('./bot/utility');
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
            nodeIntegration: true
        }
    });

    win.loadFile('web/index.html');
    initBrowser().then(async (isFirstRun) => {
        const page = await browser.newPage(); // Create a new page here and use it in both functions
        await page.setViewport({ width: 1280, height: 720 });

        if (isFirstRun) {
            await loginFacebook(page);  // Only perform login on first run
            await waitRandom(5); // wait between 1 to 5 seconds on random.
        }
        // await interactWithProfile(page); // go to profile and scroll a little bit.
        // await searchPages(page, "Pikachu");

        // let randomPikachuPage = dummyPageUrl[Math.floor(Math.random() * dummyPageUrl.length)];
        // await likePage(page, randomPikachuPage);
        // await likeRandomPost(page, randomPikachuPage);
        await watchVideos(page, "batman");

        await waitRandom(10);
        await goBackToHome(page);

        /**
         * close the browser after 10 seconds
         * 
         */
        if (browser) {
            await waitRandom(20);
            browser.close().then(() => {
                browser = null;
                app.quit();
            });
        }
    }).catch(console.error);
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
