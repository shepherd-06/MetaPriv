const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    createAccount: (username, password) => ipcRenderer.invoke('create-account', { username, password }),
    login: (username, password) => ipcRenderer.invoke('login', { username, password })
});
