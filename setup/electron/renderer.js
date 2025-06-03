const { ipcRenderer } = require('electron');

window.addEventListener('DOMContentLoaded', () => {
    const logContainer = document.getElementById('log');

    ipcRenderer.on('log', (_, message) => {
        const htmlMessage = message.replace(/\n/g, '<br>');
        logContainer.innerHTML += htmlMessage;
        logContainer.scrollTop = logContainer.scrollHeight;
    });

    ipcRenderer.send('start-setup');
});
