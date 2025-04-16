const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    runBot: () => ipcRenderer.invoke('run-bot'),
    quitApp: () => ipcRenderer.send('quit-app'),

    createAccount: (data) => ipcRenderer.invoke('create-account', data),
    loginAccount: (data) => ipcRenderer.invoke('login-account', data),

    validateSession: (sessionId) => ipcRenderer.invoke('validate-session', sessionId),

    setMasterPassword: (data) => ipcRenderer.invoke('set-master-password', data),
    verifyMasterPassword: (data) => ipcRenderer.invoke('verify-master-password', data),
});
