$(document).ready(() => {
    $('#cancel').on('click', () => {
        window.electron.closeNameWindow()
    })
    $('#name-project').on('click', () => {
        window.electron.nameProject($('#project-name').val())
    })
})