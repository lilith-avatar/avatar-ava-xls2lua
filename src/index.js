$(document).ready(() => {
    $('.root-folder').on('click', () => {
        $('#root-folder').trigger('click');
    })
    $('#root-folder').on('change', () => {
        const fakePath = document.getElementById('root-folder').files[0].path
        const folderPath = fakePath.match(/.*\\/g)
        $('#project-selector').val(null)
        //document.getElementById('kv-files').setAttribute('onclick', 'location.href=' + "'" + folderPath + "'")
        document.getElementById('root-folder-text').setAttribute('value', folderPath)
    })
    $('.output-folder').on('click', () => {
        $('#output-folder').trigger('click');
    })
    $('#output-folder').on('change', () => {
        const fakePath = document.getElementById('output-folder').files[0].path
        const folderPath = fakePath.match(/.*\\/g)
        $('#project-selector').val(null)
        //document.getElementById('kv-files').setAttribute('onclick', 'location.href=' + "'" + folderPath + "'")
        document.getElementById('output-folder-text').setAttribute('value', folderPath)
    })
    $('#trans').on('click', () => {
        if ($('#project-selector').val()) {
            sendData()
        } else {
            window.electron.sendTempData({
                "input-folder": $('#root-folder-text').val(),
                "output-folder": $('#output-folder-text').val()
            })
            window.electron.nameWindow()
        }
    })
    $('#project-selector').on('change', () => {
        window.folderChange.selectProject($('#project-selector').val())
    })
})