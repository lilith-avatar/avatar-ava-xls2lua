const {
    app,
    BrowserWindow,
    Menu,
    nativeTheme,
    dialog
} = require('electron');
const path = require('path');
const fs = require('fs');
const ipc = require('electron').ipcMain;
const {
    convertToLua
} = require('./src/xls2lua')
let win;
let nameWin;
let tmpConfigData;

function createWindow() {
    win = new BrowserWindow({
        width: 1200,
        height: 600,
        resizable: false,
        icon: './resources/Icon.png',
        webPreferences: {
            preload: path.join(__dirname, 'src', 'preload.js')
        }
    })
    nativeTheme.themeSource = 'dark'
    Menu.setApplicationMenu(null)
    win.loadFile('./views/index.html')

    //! 开发者工具
    win.webContents.openDevTools({
        mode: 'right'
    })
}

function writeConfigJson(name, data) {
    const oldData = JSON.parse(fs.readFileSync(path.join(__dirname, '.ava-x2l-config.json')))
    oldData['projects'][name] = {
        data
    }
    oldData['defaultChecked'] = name
    let newdata = JSON.stringify(oldData)
    fs.writeFileSync(path.join(__dirname, '.ava-x2l-config.json'), newdata, 'utf8')
}

app.whenReady().then(() => {
    createWindow()
    app.on('activate', function() {
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})

ipc.on('trans', () => {
    nameWin = new BrowserWindow({
        width: 600,
        height: 200,
        parent: win,
        modal: true,
        resizable: false,
        frame: false,
        webPreferences: {
            preload: path.join(__dirname, 'src', 'namepre.js')
        }
    })
    nameWin.loadFile('./views/nameWindow.html')
    //! 开发者工具
    // nameWin.webContents.openDevTools({
    //     mode: 'right'
    // })
})

ipc.on('closeNameWindow', () => {
    nameWin.close()
})

ipc.on('nameProject', async (event, name) => {
    writeConfigJson(name, tmpConfigData)
    win.webContents.send('nameComplete')
    let log = await convertToLua(tmpConfigData['input-folder'], tmpConfigData['output-folder'])
    win.webContents.send('showLog', log.error_messages)
    nameWin.close()
})

ipc.on('sendTempData', (event, data) => {
    tmpConfigData = data
})

ipc.on('sendData', async (event, data) => {
    let log = await convertToLua(data['input-folder'], data['output-folder'])
    win.webContents.send('showLog', log.error_messages)
})

ipc.on('showErrorBox', (event, title, content) => {
    dialog.showErrorBox(title, content)
})