const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    quitApp: () => ipcRenderer.send('quit-app'),

    createAccount: (data) => ipcRenderer.invoke('create-account', data),
    loginAccount: (data) => ipcRenderer.invoke('login-account', data),

    validateSession: (sessionId) => ipcRenderer.invoke('validate-session', sessionId),

    setMasterPassword: (data) => ipcRenderer.invoke('set-master-password', data),
    verifyMasterPassword: (data) => ipcRenderer.invoke('verify-master-password', data),

    submitFacebookAuth: (data) => ipcRenderer.invoke('submit-facebook-auth', data),

    // 🆕 Bot process handling
    runBot: (sessionId) => ipcRenderer.invoke('run-bot', sessionId),
    isBotRunning: () => ipcRenderer.invoke('is-bot-running'),
    stopBot: () => ipcRenderer.invoke('stop-bot'),
});
