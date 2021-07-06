const {
    app,
    BrowserWindow,
    Menu
} = require('electron');

function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 400
    })
    Menu.setApplicationMenu(null)
    win.loadFile('index.html')
}

app.whenReady().then(() => {
    createWindow()
    app.on('activate', function() {
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})