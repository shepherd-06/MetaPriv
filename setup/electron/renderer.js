const { ipcRenderer } = require('electron');

window.addEventListener('DOMContentLoaded', () => {
    const logContainer = document.getElementById('log');
    ipcRenderer.on('log', (_, message) => {
        logContainer.textContent += message;
        logContainer.scrollTop = logContainer.scrollHeight;
    });

    ipcRenderer.send('start-setup');
});
