require('dotenv').config();
const { waitRandom, waitMust } = require('./utility');


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

async function searchPages(page, keywords) {
    console.log(`Searching pages for keyword: ${keywords}`);
    let pageURLs = [];

    try {
        // Navigate to Facebook's search page for pages with the specified keywords
        await page.goto(`https://www.facebook.com/search/pages/?q=${keywords}`);
        await waitMust(15); // Wait for initial content load

        // Scroll to the bottom of the page four times to load more content
        for (let i = 0; i < 4; i++) {
            await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
            await waitMust(10); // wait for the next batch of data to load
        }

        // Scroll back to the top of the page
        await page.evaluate(() => window.scrollTo(0, 0));
        await waitMust(5); // ensure the page has settled

        // Select all anchor elements that contain the specific URL ending
        const links = await page.$$(`a[href*="?__tn__=%3C"]`);

        // Convert link elements to their href attributes
        for (let link of links) {
            const url = await (await link.getProperty('href')).jsonValue();
            if (url.includes('facebook.com')) {
                pageURLs.push(url);
            }
        }
        console.log('Found URLs:', pageURLs);
        /**
         * TODO: save pageURLs in database.
         */
        await waitRandom(20);
    } catch (error) {
        console.error('An error occurred while searching for pages:', error);
    }
    return pageURLs;
}


async function likePage(page, pageUrl) {
    /**
     * Like/Follow the page from the URL.
     * Store the pageName in the database
     */
    try {
        await page.goto(pageUrl);
        await waitMust(10); // Adjust wait time as necessary for the page to load

        // Get the page name
        const pageName = await page.$eval('h1.html-h1', el => el.innerText.trim());

        // Check if the Like button is present
        const likeButton = await page.$('div[aria-label="Like"]');
        if (likeButton) {
            await likeButton.click();
            console.log(`Liked page: ${pageName}`);
        } else {
            // If Like button isn't found, look for the Follow button
            const followButton = await page.$('div[aria-label="Follow"]');
            if (followButton) {
                await followButton.click();
                console.log(`Followed page: ${pageName}`);
            }
        }
        await waitRandom(20);
        // Log the action and the page name
        console.log(`Action completed on: ${pageName}`);

    } catch (error) {
        console.error(`An error occurred while processing ${pageUrl}:`, error);
    }
}


module.exports = {
    loginFacebook,
    interactWithProfile,
    goBackToHome,
    searchPages,
    likePage,
};