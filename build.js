const {
    MSICreator
} = require('electron-wix-msi');
const path = require('path');

// 2. Define input and output directory.
// Important: the directories must be absolute, not relative e.g
// appDirectory: "C:\\Users\sdkca\Desktop\OurCodeWorld-win32-x64", 
const APP_DIR = path.resolve(__dirname, './App/ava-x2l-win32-x64');
// outputDirectory: "C:\\Users\sdkca\Desktop\windows_installer", 
const OUT_DIR = path.resolve(__dirname, './App/windows_installer');



// Step 1: Instantiate the MSICreator
const msiCreator = new MSICreator({
    appDirectory: APP_DIR,
    description: 'My amazing Kitten simulator',
    exe: 'ava-x2l',
    name: 'ava-x2l',
    manufacturer: 'Kitten Technologies',
    version: '1.1.2',
    outputDirectory: OUT_DIR,
    appIconPath: 'icon.ico',
    ui: {
        chooseDirectory: true
    }
});

const run = async () => {
    // Step 2: Create a .wxs template file
    const supportBinaries = await msiCreator.create();
    console.log(typeof(supportBinaries));
    // 🆕 Step 2a: optionally sign support binaries if you
    // sign you binaries as part of of your packaging script
    // supportBinaries.foreach(async (binary) => {
    //     // Binaries are the new stub executable and optionally
    //     // the Squirrel auto updater.
    //     await signFile(binary);
    // });

    // Step 3: Compile the template to a .msi file
    await msiCreator.compile();
}

run()