const {
    app,
    BrowserWindow,
    Menu,
    nativeTheme
} = require('electron');
const fs = require('fs');
const path = require('path');

function createWindow() {
    const win = new BrowserWindow({
        width: 1200,
        height: 600,
        resizable: false,
        icon: './resources/Icon.png',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js')
        }
    })
    nativeTheme.themeSource = 'dark'
    Menu.setApplicationMenu(null)
    win.loadFile('index.html')
}

app.whenReady().then(() => {
    createWindow()
    app.on('activate', function() {
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})