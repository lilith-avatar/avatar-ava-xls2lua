$(document).ready(() => {
    $('#cancel').on('click', () => {
        window.electron.closeNameWindow()
    })
    $('#name-project').on('click', () => {
        if (!($('#project-name').val())) {
            window.electron.showErrorBox('error', '还没有命名')
        } else {
            window.electron.nameProject($('#project-name').val())
        }
    })
})