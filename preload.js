const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    // app management
    quitApp: () => ipcRenderer.send('quit-app'),

    // account
    createAccount: (data) => ipcRenderer.invoke('create-account', data),
    loginAccount: (data) => ipcRenderer.invoke('login-account', data),
    submitFacebookAuth: (data) => ipcRenderer.invoke('submit-facebook-auth', data),

    // session
    validateSession: (sessionId) => ipcRenderer.invoke('validate-session', sessionId),
    invalidateSession: (sessionId) => ipcRenderer.invoke('invalidate-session', sessionId),

    // master password
    setMasterPassword: (data) => ipcRenderer.invoke('set-master-password', data),
    verifyMasterPassword: (data) => ipcRenderer.invoke('verify-master-password', data),

    // 🆕 Bot process handling
    runBot: (sessionId) => ipcRenderer.invoke('run-bot', sessionId),
    isBotRunning: () => ipcRenderer.invoke('is-bot-running'),
    stopBot: () => ipcRenderer.invoke('stop-bot'),

    // KeyWords
    fetchKeywords: (sessionId) => ipcRenderer.invoke('fetch-keywords', sessionId),
    addKeywords: (data) => ipcRenderer.invoke('add-keywords', data),

    // Logs
    fetchRecentLogs: (data) => ipcRenderer.invoke('fetch-recent-logs', data),
    fetchAllLogs: (sessionId) => ipcRenderer.invoke('activity-logs', sessionId),


});
