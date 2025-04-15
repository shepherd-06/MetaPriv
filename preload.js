const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  runBot: () => ipcRenderer.invoke('run-bot'),
  quitApp: () => ipcRenderer.send('quit-app')
});
