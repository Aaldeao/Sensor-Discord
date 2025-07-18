//------ Para exportar la aplicacion des-comente el siguiente bloque de código de codigo, de lo contrario funcionara en modo desarrollo ------//
/*
import { app, BrowserWindow, Tray, Menu } from 'electron';
import { fork } from 'child_process';
import path from 'path';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let mainWindow;
let backendProcess;
let tray;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        title: 'Sensor bGames',
        resizable: false,
        maximizable: false,
        icon: join(__dirname, 'icono.ico'), // Ahora sí puedes usar 'join'
        webPreferences: {
            contextIsolation: true,
            nodeIntegration: false,
        },
    });

    //mainWindow.loadURL('http://localhost:6969');

    // Oculta la ventana en vez de cerrarla
    mainWindow.on('close', (e) => {
        e.preventDefault();
        mainWindow.hide();
    });

    // Levantar el backend como un proceso hijo
    const backendPath = path.join(__dirname, '../server.js');
    backendProcess = fork(backendPath);

    backendProcess.on('error', (error) => {
        console.error('Error en el backend:', error.message);
    });

    backendProcess.on('message', (msg) => {
        if (msg === 'backend-ready') {
            // Cargar el frontend empaquetado por Vite
            const viteDistPath = path.join(__dirname, '../dist/index.html');
            mainWindow.loadFile(viteDistPath);
        }
    });

    // Cerrar backend al cerrar la aplicación
    mainWindow.on('closed', () => {
        mainWindow = null;
        if (backendProcess) {
            backendProcess.kill();
        }
    });
}

app.on('ready', () => { 
    createWindow();

    tray = new Tray(join(__dirname, 'icono.ico'));
    const contextMenu = Menu.buildFromTemplate([
        { label: 'Show', click: () => mainWindow.show() },
        {
            label: 'Close', click: () => {
                tray.destroy();
                app.quit();
            }
        }
    ]);
    tray.setToolTip('Sensor bGames');
    tray.setContextMenu(contextMenu);

    app.setLoginItemSettings({
        openAtLogin: false,
    });
});


app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

//------ Para exportar la aplicacion des-comente el bloque de código de arriba -----//
*/ 

//------ Bloque de codigo para ejecutar la aplicacion en modo desarrollo ------//
import { app, BrowserWindow, Tray, Menu } from 'electron';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path'; // Importa 'join' desde 'path'

import { spawn } from 'child_process';
import { fork } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let mainWindow;
let tray;

let botProcess; // Proceso del bot de Discord
let serverProcess; // Proceso del servidor para la autenticacion de Discord

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        resizable: false,
        maximizable: false,
        icon: join(__dirname, 'icono.ico'), // Ahora sí puedes usar 'join'
        webPreferences: {
            contextIsolation: true,
            nodeIntegration: false,
        },
    });

    mainWindow.loadURL('http://localhost:6969');

    // Ejecutar el bot de Discord
    const botPath = join(__dirname, '../bot/bot.py');
    botProcess = spawn('python', [botPath]);

    botProcess.stdout.on('data', (data) => {
        console.log(`[BOT]: ${data.toString().trim()}`);
    });

    botProcess.stderr.on('data', (data) => {
        const msg = data.toString().trim();
        if (msg.startsWith('[INFO]') || msg.startsWith('[DEBUG')) {
            console.log(`[BOT INFO]: ${msg}`);
        } else if (msg.startsWith('[ERROR') || msg.startsWith('[CRITICAL')) {
            console.error(`[BOT ERROR]: ${msg}`);
        } else {
            console.log(`[BOT INFO]: ${msg}`);
        }
    });

    botProcess.on('close', (code) => {
        console.log(`Bot process exited with code ${code}`);
    });

    // Oculta la ventana en vez de cerrarla
    mainWindow.on('close', (e) => {
        e.preventDefault();
        mainWindow.hide();
    });
}

app.on('ready', () => {
    serverProcess = fork(join(__dirname, '../bot/authServer.js')); // Ejcuta /Levanta el servidor de autenticación de Discord
    createWindow();

    tray = new Tray(join(__dirname, 'icono.ico'));
    const contextMenu = Menu.buildFromTemplate([
        { label: 'Mostrar', click: () => mainWindow.show() },
        { label: 'Salir', click: () => {
            tray.destroy();
            if (serverProcess) {
                serverProcess.kill(); // Cierra el proceso del servidor de autenticación
            }
            app.quit();
        } }
    ]);
    tray.setToolTip('Mi App en Segundo Plano');
    tray.setContextMenu(contextMenu);

    app.setLoginItemSettings({
        openAtLogin: true,
    });
});

app.on('window-all-closed', (e) => {
    e.preventDefault();
});

app.on('will-quit', () => {
    if (serverProcess) serverProcess.kill();
});