require('dotenv').config();
const { waitRandom, waitMust } = require('./utility');
const { getFacebookCredentials } = require('../database/users');
const { getARandomKeyword } = require('../database/keywords');
const { addAPage, getARandomPageUrl, markPageAsLiked } = require('../database/pages');
const { addAVideo } = require("../database/videos");

const { writeLog } = require('../utility/logmanager');


async function loginFacebook(page, sessionId, masterPassword) {
    try {
        await page.goto('https://www.facebook.com');
        await waitRandom(10);

        const cookieButtonSelector = 'div[role="none"].x1ja2u2z.x78zum5.x2lah0s.x1n2onr6.xl56j7k.x6s0dn4.xozqiw3.x1q0g3np.xi112ho.x17zwfj4.x585lrc.x1403ito.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xn6708d.x1ye3gou.xtvsq51.x1r1pt67 div[role="none"] span[dir="auto"]';
        const cookieButton = await page.$(cookieButtonSelector);
        if (cookieButton) await cookieButton.click();

        const fb_data = await getFacebookCredentials(sessionId);
        // possibility to ask for the current users computer password to unlock the credential,
        if (!fb_data.success) {
            writeLog(`❌ Facebook credentials : ${fb_data.message}`, masterPassword);
            // TODO: ideally i should exit the app here or something!
            return;
        }
        const fb_email = fb_data.email;
        const fb_pass = fb_data.password;

        await new Promise(resolve => setTimeout(resolve, 1000));
        await page.type('#email', fb_email, { delay: 30 });
        await waitRandom(10);
        await page.type('#pass', fb_pass, { delay: 30 });
        await waitRandom(10);
        await page.click('button[name="login"]');

        // at least 10 seconds waiting.
        await waitMust(20);
        // Commented out to prevent automatic navigation wait
        writeLog('Logged in or still on login page for debugging.', masterPassword);
    } catch (error) {
        writeLog(`An error occurred ${error}`, masterPassword);
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

async function goBackToHome(page, masterPassword) {
    /**
     * function to go back home when needed.
     */
    try {
        writeLog("Attempting to click the Facebook logo...", masterPassword);
        const logoSelector = 'a[aria-label="Facebook"]';
        await page.click(logoSelector);
        writeLog("Facebook logo clicked successfully. Refreshing home or going back to home", masterPassword);
        await waitMust(10); // Wait 10 seconds
    } catch (error) {
        writeLog(`An error occurred while trying to click the Facebook logo: ${error}`, masterPassword);
    }
}

async function searchPages(page, userId) {
    // First get a random keyword from the database.
    const { keyword, id } = await getARandomKeyword(userId);
    console.log(`Searching pages for keyword: ${keyword} with id ${id}`);
    let pageURLs = [];

    try {
        // Navigate to Facebook's search page for pages with the specified keywords
        await page.goto(`https://www.facebook.com/search/pages/?q=${keyword}`);
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
         * Save pageURLs in database.
         */
        if (pageURLs.length > 0) {
            for (const url of pageURLs) {
                await addAPage({
                    keywordId: id,
                    pageUrl: url,
                    isLiked: 0
                });
            }
        }
        await waitRandom(20);
    } catch (error) {
        console.error('An error occurred while searching for pages:', error);
    }
    return pageURLs;
}

async function likePage(page, userId) {
    /**
     * Like/Follow the page from the URL.
     * Store the pageName in the database
     */
    try {
        const pageUrl = await getARandomPageUrl();
        console.log("Going to page : ", pageUrl);
        if (pageUrl == null) {
            console.log("pageUrl came null");
            return
        }
        let status = false;
        await page.goto(pageUrl);
        await waitMust(10); // Adjust wait time as necessary for the page to load

        // Get the page name
        const pageName = await page.$eval('h1.html-h1', el => el.innerText.trim());

        // Check if the Like button is present
        const likeButton = await page.$('div[aria-label="Like"]');
        if (likeButton) {
            await likeButton.click();
            console.log(`Liked page: ${pageName}`);
            status = true;
        } else {
            // If Like button isn't found, look for the Follow button
            const followButton = await page.$('div[aria-label="Follow"]');
            if (followButton) {
                await followButton.click();
                console.log(`Followed page: ${pageName}`);
                status = true;
            }
        }
        await waitRandom(20);
        if (status) {
            await markPageAsLiked(pageUrl);
            // Log the action and the page name
            console.log(`Action completed on: ${pageName}`);
        }
    } catch (error) {
        console.error(`An error occurred while processing pageUrl:`, error);
    }
}

async function generateRandomInteraction(page) {
    /**
     * Incomplete Func.
     * this function is supposed to create some random interaction on home screen 
     * at some point.
     */
    try {
        await page.goto("https://facebook.com");
        await waitMust(10);

        let pos = 1;
        while (true) {
            const selector = `div.x1a2a7pz[aria-posinset="${pos}"]`;
            const element = await page.$(selector);

            if (!element) {
                console.log(`No more posts found at aria-posinset="${pos}". Stopping.`);
                break;
            }

            const html = await element.evaluate(el => el.innerHTML);
            console.log(`Post #${pos}: \n`, html);
            pos++;

            await page.evaluate(() => window.scrollBy(0, 200));
            await waitMust(3); // simulate human pause
            await waitRandom(10);
            if (pos == 5) {
                break
            }
        }

    } catch (error) {
        console.log("Oh no! I failed! ", error);
    }
}


async function likeRandomPost(page) {
    const pageUrl = await getARandomPageUrl(1);
    console.log("Going to page : ", pageUrl);
    await page.goto(pageUrl);
    await waitMust(10);

    let likeCount = 0;
    const randomBreak = Math.floor(Math.random() * 1) + 4; // Between 
    const seenElements = new Set();

    while (true) {
        // Step 2: Get all post elements
        const postElements = await page.$$('div.x1n2onr6.x1ja2u2z'); // this is the article wrapper
        let newPostFound = false;

        for (let postElement of postElements) {
            const uniqueId = await postElement.evaluate(el => el.innerText.slice(0, 50)); // crude fingerprint
            if (seenElements.has(uniqueId)) continue;
            seenElements.add(uniqueId);
            newPostFound = true;
            console.log(uniqueId);

            // Scroll into view
            await postElement.evaluate(el => el.scrollIntoView({ behavior: 'smooth', block: 'center' }));
            await waitRandom(3);
            await waitMust(10);

            // Step 3: Check if already liked (presence of 'Remove Like' button)
            const alreadyLiked = await postElement.$('div[aria-label="Remove Like"]');
            if (alreadyLiked) {
                continue;
            }

            // Step 4: Randomly decide whether to like
            if (Math.random() > Math.random()) {
                const likeBtn = await postElement.$('div[aria-label="Like"]');
                if (likeBtn) {
                    try {
                        await likeBtn.click();
                        likeCount++;

                        console.log(`✅ Liked post #${likeCount}`);

                        // Optional: Get post URL for logging
                        const postLink = await postElement.$('a[role="link"]');
                        if (postLink) {
                            const postUrl = await (await postLink.getProperty('href')).jsonValue();
                            console.log(`Liked post: ${postUrl}`);
                        }

                        // Short wait after liking
                        await waitMust(10);
                    } catch (e) {
                        console.error(`Failed to like post:`, e);
                    }
                }
            } else {
                console.log("Skipping Like");
            }

            if (likeCount >= randomBreak) {
                console.log(`🔁 Random break reached after ${likeCount} likes.`);
                return;
            }
        }

        if (!newPostFound) {
            console.log(`No more new posts found. Ending.`);
            break;
        }

        // Scroll down to load more posts
        await page.evaluate(() => window.scrollBy(0, window.innerHeight));
        await waitMust(15);
    }
}

async function watchVideos(page, userId) {
    /**
     * We watch videos here from the keyword.
     */
    try {
        const { keyword, id } = await getARandomKeyword(userId);
        console.log(`Searching pages for keyword: ${keyword}`);
        const url = `https://www.facebook.com/watch/search/?q=${keyword}`;
        await page.goto(url);
        await waitMust(10);
        await waitRandom(2);

        // Scroll and track videos
        const seen = new Set();
        // const maxVideos = Math.floor(Math.random() * 8) + 6; // 6 to 13
        const maxVideos = 2; // watch 2 videos during test.
        let watched = 0;

        while (watched < maxVideos) {
            await waitMust(10);
            await waitRandom(2);

            const videoElements = await page.$$('div.x1yztbdb');
            let newVideos = [];

            for (let i = 0; i < videoElements.length; i++) {
                const html = await videoElements[i].evaluate(el => el.innerText.slice(0, 50));
                if (!seen.has(html)) {
                    newVideos.push(videoElements[i]);
                    seen.add(html);
                }
            }

            if (newVideos.length === 0) {
                console.log('No more new videos to watch.');
                break;
            }

            for (let videoElement of newVideos) {
                if (watched >= maxVideos) break;

                try {
                    await videoElement.evaluate(el => el.scrollIntoView({ behavior: 'smooth', block: 'center' }));
                    await waitMust(5);
                    await waitRandom(3);

                    const videoLengthHandle = await videoElement.$('span.x193iq5w.xeuugli.x13faqbe');
                    if (!videoLengthHandle) continue;

                    const videoLength = await videoLengthHandle.evaluate(el => el.textContent);
                    if (videoLength === 'LIVE') continue;

                    const links = await videoElement.$$('a[role="link"]');
                    if (links.length < 2) continue;

                    const postUrl = await links[0].evaluate(el => el.href.split('&external_log_id')[0]);
                    const pageUrl = await links[1].evaluate(el => el.href);

                    console.log(`▶️ Watching video: ${videoLength}`);
                    console.log(`🔗 Post: ${postUrl}`);
                    console.log(`📄 Page: ${pageUrl}`);

                    await videoLengthHandle.click();
                    await waitMust(5);
                    await waitRandom(5);

                    let delta = 30;
                    const parts = videoLength.split(':').map(n => parseInt(n));
                    if (parts.length === 2) delta = parts[0] * 60 + parts[1];
                    else if (parts.length === 3) delta = parts[0] * 3600 + parts[1] * 60 + parts[2];

                    const watchTime = 5 + delta;
                    console.log("WatchTime: ", watchTime, " sec");
                    // await waitMust(watchTime / 2);
                    await waitMust(12); // watch it less time than needed during test. 
                    await waitRandom(12);
                    let isLiked = 0;

                    if (Math.random() < Math.random()) {
                        try {
                            const likeBtn = await page.$('div[aria-label="Like"]');
                            if (likeBtn) {
                                await likeBtn.click();
                                console.log('👍 Liked video');
                                isLiked = 1;
                            }
                        } catch (e) {
                            console.log('⚠️ Like button not found.');
                        }
                    } else {
                        console.log('❌ Skipping Liking video');
                    }

                    const status = await addAVideo({
                        post_URL: postUrl,
                        page_URL: pageUrl,
                        keyword: keyword,
                        userId: userId,
                        screenshot_name: "",
                        liked: isLiked
                    });
                    console.log(status.message);

                    // await waitMust(watchTime / 2);
                    await waitRandom(5);
                    await page.goBack();
                    await waitMust(10);
                    watched++;

                } catch (err) {
                    console.error('❌ Error watching video:', err);
                    continue;
                }
            }
        }
        console.log('✅ Finished watching videos.');
    } catch (err) {
        console.error(`An error occurred while watching video :`, error);
    }
}



module.exports = {
    loginFacebook,
    interactWithProfile,
    goBackToHome,
    searchPages,
    likePage,
    likeRandomPost,
    watchVideos,
    generateRandomInteraction,
};