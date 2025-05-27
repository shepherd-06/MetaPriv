const { app, BrowserWindow, ipcMain } = require('electron');
const { exec } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'renderer.js'),
            contextIsolation: false,
            nodeIntegration: true
        }
    });

    mainWindow.loadFile(path.join(__dirname, 'index.html'));
}

app.whenReady().then(createWindow);

ipcMain.on('start-setup', (event) => {
    const INSTALL_DIR = path.join(app.getPath('home'), 'Library', 'MetaPriv');
    const GIT_REPO = 'https://github.com/shepherd-06/MetaPriv.git';
    const GIT_TARGET_BRANCH = 'dev';

    function log(message) {
        event.sender.send('log', message);
    }

    function findExecutable(name) {
        const searchPaths = [
            '/usr/local/bin',
            '/usr/bin',
            '/opt/homebrew/bin',
            '/bin',
            '/opt/local/bin',
            '/snap/bin'
        ];
        for (const dir of searchPaths) {
            const fullPath = path.join(dir, name);
            if (fs.existsSync(fullPath) && fs.statSync(fullPath).isFile()) {
                log(`✅ Found ${name} at ${fullPath}`);
                return fullPath;
            }
        }
        log(`❌ ${name} not found in system paths.`);
        return null;
    }

    const NODE_PATH = findExecutable('node');
    const NPM_PATH = findExecutable('npm');

    // Fix the PATH for subprocesses
    const extraDirs = [
        '/usr/local/bin',
        '/opt/homebrew/bin',
        '/usr/bin',
        '/bin',
        '/opt/local/bin',
        '/snap/bin'
    ];
    const nodeDir = NODE_PATH ? path.dirname(NODE_PATH) : '';
    const npmDir = NPM_PATH ? path.dirname(NPM_PATH) : '';
    const newPaths = Array.from(new Set([nodeDir, npmDir, ...extraDirs]));
    process.env.PATH = `${newPaths.join(':')}:${process.env.PATH}`;

    function runCommand(cmd, cwd = process.cwd()) {
        return new Promise((resolve, reject) => {
            log(`🔧 Running: ${cmd}`);
            const child = exec(cmd, { cwd, env: process.env });
            child.stdout.on('data', (data) => log(data.toString()));
            child.stderr.on('data', (data) => log(data.toString()));
            child.on('close', (code) => {
                if (code === 0) resolve();
                else reject(new Error(`Command failed: ${cmd}`));
            });
        });
    }

    async function setup() {
        try {
            log('🚀 Starting MetaPriv Setup...\n');

            if (!NODE_PATH || !NPM_PATH) {
                throw new Error('Node.js or npm not found. Please install them and try again.');
            }

            log('🔍 Checking Node.js...');
            await runCommand(`${NODE_PATH} -v`);

            log('🔍 Checking npm...');
            await runCommand(`${NPM_PATH} -v`);

            if (fs.existsSync(path.join(INSTALL_DIR, '.git'))) {
                log(`📁 MetaPriv already exists at ${INSTALL_DIR}`);
                await runCommand('git fetch', INSTALL_DIR);
                await runCommand(`git checkout ${GIT_TARGET_BRANCH}`, INSTALL_DIR);
                await runCommand('git pull', INSTALL_DIR);
            } else {
                log(`📥 Cloning MetaPriv (${GIT_TARGET_BRANCH})...`);
                await runCommand(`git clone --branch ${GIT_TARGET_BRANCH} --depth 1 ${GIT_REPO} "${INSTALL_DIR}"`);
            }

            await runCommand(`${NPM_PATH} install`, INSTALL_DIR);

            const frontendDir = path.join(INSTALL_DIR, 'frontend');
            if (fs.existsSync(frontendDir)) {
                await runCommand(`${NPM_PATH} install`, frontendDir);
                await runCommand(`${NPM_PATH} run build`, frontendDir);
            } else {
                log('⚠️ No frontend directory found. Skipping frontend build.');
            }

            log('\n🎉 Setup Complete! Launching MetaPriv...');

            const launchCommand = `cd "${INSTALL_DIR}" && ${NPM_PATH} start`;

            if (process.platform === 'darwin') {
                // Escape backslashes and double quotes for AppleScript
                const appleScriptCommand = launchCommand
                    .replace(/\\/g, '\\\\')    // Escape backslashes
                    .replace(/"/g, '\\"');     // Escape double quotes

                await runCommand(`osascript -e 'tell application "Terminal" to do script "${appleScriptCommand}"'`);
            } else if (process.platform === 'linux') {
                await runCommand(`gnome-terminal -- bash -c "${launchCommand}"`).catch(() =>
                    runCommand(`xterm -e "${launchCommand}"`)
                );
            } else if (process.platform === 'win32') {
                log(`⚠️ On Windows, please manually run:\n   ${launchCommand}`);
            }


            log('✅ All done!');

        } catch (err) {
            log(`❌ Error: ${err.message}`);
        }
    }

    setup();
});
