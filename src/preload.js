const fs = require('fs');
const path = require('path');

window.addEventListener('DOMContentLoaded', () => {
    isFirstTime()
})

function isFirstTime() {
    try {
        const configPath = path.join(__dirname, '..', '.ava-x2l-config.json')
        const configJson = fs.readFileSync(configPath, 'utf8')
        const config = JSON.parse(configJson)
        return config
    } catch (e) {
        fs.writeFileSync(path.join(__dirname, '..', '.ava-x2l-config.json'), '{}')
    }
}