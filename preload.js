const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    createAccount: (username, password) => ipcRenderer.invoke('create-account', { username, password }),
    login: (username, password) => ipcRenderer.invoke('login', { username, password }),
    saveCredentials: (username, password) => ipcRenderer.invoke('save-credentials', { username, password }),
    getCredentials: (username) => ipcRenderer.invoke('get-credentials', username),
    logout: () => ipcRenderer.invoke('logout')
});
