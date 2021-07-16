const {
    ipcRenderer,
    contextBridge
} = require('electron');

contextBridge.exposeInMainWorld(
    'electron', {
        nameWindow: () => ipcRenderer.send('trans'),
        closeNameWindow: () => ipcRenderer.send('closeNameWindow'),
        sendTempData: data => ipcRenderer.send('sendTempData', data),
        nameProject: name => ipcRenderer.send('nameProject', name),
        showErrorBox: (title, content) => ipcRenderer.send('showErrorBox', title, content)
    }
)