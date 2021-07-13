const {
    ipcRenderer,
    contextBridge
} = require('electron');
const fs = require('fs');
const path = require('path');

function selectByValue(value) {
    const options = document.getElementById("project-selector").options
    for (let key in options) {
        if (options[key].value === value) {
            return key
        }
    }
    return 0
}

window.addEventListener('DOMContentLoaded', () => {
    try {
        const data = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '.ava-x2l-config.json'), 'utf8'))
        const selector = document.getElementById("project-selector")
        const inputFolder = document.getElementById("root-folder-text")
        const outputFolder = document.getElementById("output-folder-text")
        for (let key in data["projects"]) {
            selector.innerHTML = selector.innerHTML + `<option value ='${key}'>${key}</option>`
        }
        selector.options[selectByValue(data["defaultChecked"])].selected = true;
        inputFolder.setAttribute('value', data["projects"][data["defaultChecked"]]['data']['input-folder'])
        outputFolder.setAttribute('value', data["projects"][data["defaultChecked"]]['data']['output-folder'])
    } catch (e) {
        console.log(e);
        fs.writeFileSync(path.join(__dirname, '..', '.ava-x2l-config.json'), '{"projects":{},"defaultChecked":""}', 'utf8')
    }
})

contextBridge.exposeInMainWorld(
    'electron', {
        nameWindow: () => ipcRenderer.send('trans'),
        closeNameWindow: () => ipcRenderer.send('closeNameWindow'),
        sendTempData: data => ipcRenderer.send('sendTempData', data),
        nameProject: name => ipcRenderer.send('nameProject', name)
    }
)

contextBridge.exposeInMainWorld(
    'folderChange', {
        selectProject: (project) => {
            const data = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '.ava-x2l-config.json'), 'utf8'))
            document.getElementById('root-folder-text').setAttribute('value', data['projects'][project]['data']['input-folder'])
            document.getElementById('output-folder-text').setAttribute('value', data['projects'][project]['data']['output-folder'])
        }
    }
)

ipcRenderer.on('nameComplete', () => {
    const data = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '.ava-x2l-config.json'), 'utf8'))
    const selector = document.getElementById("project-selector")
    selector.innerHTML = ``
    for (let key in data["projects"]) {
        selector.innerHTML = selector.innerHTML + `<option value ='${key}'>${key}</option>`
    }
    selector.options[selectByValue(data["defaultChecked"])].selected = true;
})