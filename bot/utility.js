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

module.exports = {
    waitRandom,
    waitMust,
};