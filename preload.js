const fs = require('fs');
const path = require('path');

window.addEventListener('DOMContentLoaded', () => {
    const replaceInputFiled = (selector, text) => {
        const element = document.getElementById(selector);
        if (element) element.setAttribute("value", text)
    }
    const configPath = path.join(__dirname, '.ava-x2l-config.json')
    const configJson = fs.readFileSync(configPath, 'utf8')
    const config = JSON.parse(configJson)
    for (var key in config) {
        replaceInputFiled(key, config[key])
    }
})