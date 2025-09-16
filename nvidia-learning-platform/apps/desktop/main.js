const { app, BrowserWindow, Menu, Tray, dialog, ipcMain, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const Store = require('electron-store');
const { autoUpdater } = require('electron-updater');

// Configure electron store for local data
const store = new Store({
  defaults: {
    appMode: 'hybrid', // online, offline, hybrid
    userData: {
      role: null,
      completedCourses: [],
      currentPath: null
    },
    preferences: {
      theme: 'dark',
      notifications: true,
      autoUpdate: true
    }
  }
});

class NvidiaLearningDesktop {
  constructor() {
    this.mainWindow = null;
    this.splashWindow = null;
    this.tray = null;
    this.backendProcess = null;
    this.isQuitting = false;
  }

  async init() {
    // Single instance lock
    const gotTheLock = app.requestSingleInstanceLock();
    if (!gotTheLock) {
      app.quit();
      return;
    }

    // Show splash screen
    this.createSplashWindow();

    await app.whenReady();

    // Start services
    await this.startBackendServices();

    // Create main window
    setTimeout(() => {
      this.createMainWindow();
      this.closeSplashWindow();
    }, 3000);

    // Setup system tray
    this.setupSystemTray();

    // Setup auto-updater
    if (store.get('preferences.autoUpdate')) {
      this.setupAutoUpdater();
    }

    // Handle app events
    this.handleAppEvents();
  }

  createSplashWindow() {
    this.splashWindow = new BrowserWindow({
      width: 600,
      height: 400,
      frame: false,
      alwaysOnTop: true,
      transparent: true,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true
      }
    });

    this.splashWindow.loadFile(path.join(__dirname, 'splash.html'));
  }

  closeSplashWindow() {
    if (this.splashWindow) {
      this.splashWindow.close();
      this.splashWindow = null;
    }
  }

  createMainWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1400,
      height: 900,
      minWidth: 1200,
      minHeight: 700,
      title: 'NVIDIA Learning Platform',
      icon: path.join(__dirname, 'assets', 'icon.ico'),
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
      },
      show: false
    });

    // Load the app based on mode
    const appMode = store.get('appMode');
    if (appMode === 'offline') {
      // Load local build
      this.mainWindow.loadFile(
        path.join(__dirname, '../pathway-visualizer/dist/index.html')
      );
    } else {
      // Try to load from local server first, fallback to built files
      this.mainWindow.loadURL('http://localhost:5173').catch(() => {
        this.mainWindow.loadFile(
          path.join(__dirname, '../pathway-visualizer/dist/index.html')
        );
      });
    }

    // Show window when ready
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow.show();

      // Open DevTools in development
      if (process.env.NODE_ENV === 'development') {
        this.mainWindow.webContents.openDevTools();
      }
    });

    // Setup menu
    this.setupApplicationMenu();

    // Handle window events
    this.mainWindow.on('close', (event) => {
      if (!this.isQuitting) {
        event.preventDefault();
        this.mainWindow.hide();

        // Show notification
        if (process.platform === 'win32') {
          this.tray.displayBalloon({
            title: 'NVIDIA Learning Platform',
            content: 'Application minimized to system tray'
          });
        }
      }
    });

    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });
  }

  async startBackendServices() {
    const appMode = store.get('appMode');

    if (appMode !== 'online') {
      // Start local backend server
      console.log('Starting local backend server...');

      this.backendProcess = spawn('node', [
        path.join(__dirname, '../backend/dist/index.js')
      ], {
        env: {
          ...process.env,
          PORT: 3001,
          DATABASE_URL: 'sqlite://./data/learning.db',
          NODE_ENV: 'production'
        }
      });

      this.backendProcess.stdout.on('data', (data) => {
        console.log(`Backend: ${data}`);
      });

      this.backendProcess.stderr.on('data', (data) => {
        console.error(`Backend Error: ${data}`);
      });
    }
  }

  setupSystemTray() {
    const trayIcon = path.join(__dirname, 'assets', 'tray-icon.png');
    this.tray = new Tray(trayIcon);
    this.tray.setToolTip('NVIDIA Learning Platform');

    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Show App',
        click: () => {
          if (this.mainWindow) {
            this.mainWindow.show();
          }
        }
      },
      {
        label: 'Mode',
        submenu: [
          {
            label: 'Online',
            type: 'radio',
            checked: store.get('appMode') === 'online',
            click: () => this.switchMode('online')
          },
          {
            label: 'Offline',
            type: 'radio',
            checked: store.get('appMode') === 'offline',
            click: () => this.switchMode('offline')
          },
          {
            label: 'Hybrid',
            type: 'radio',
            checked: store.get('appMode') === 'hybrid',
            click: () => this.switchMode('hybrid')
          }
        ]
      },
      { type: 'separator' },
      {
        label: 'Check for Updates',
        click: () => this.checkForUpdates()
      },
      { type: 'separator' },
      {
        label: 'Quit',
        click: () => {
          this.isQuitting = true;
          app.quit();
        }
      }
    ]);

    this.tray.setContextMenu(contextMenu);

    // Double-click to show
    this.tray.on('double-click', () => {
      if (this.mainWindow) {
        this.mainWindow.show();
      }
    });
  }

  setupApplicationMenu() {
    const template = [
      {
        label: 'File',
        submenu: [
          {
            label: 'Import Progress',
            accelerator: 'CmdOrCtrl+O',
            click: () => this.importProgress()
          },
          {
            label: 'Export Progress',
            accelerator: 'CmdOrCtrl+S',
            click: () => this.exportProgress()
          },
          { type: 'separator' },
          {
            label: 'Preferences',
            accelerator: 'CmdOrCtrl+,',
            click: () => this.openPreferences()
          },
          { type: 'separator' },
          {
            label: 'Exit',
            accelerator: 'CmdOrCtrl+Q',
            click: () => {
              this.isQuitting = true;
              app.quit();
            }
          }
        ]
      },
      {
        label: 'View',
        submenu: [
          {
            label: 'Reload',
            accelerator: 'CmdOrCtrl+R',
            click: () => {
              this.mainWindow.reload();
            }
          },
          {
            label: 'Toggle DevTools',
            accelerator: 'F12',
            click: () => {
              this.mainWindow.webContents.toggleDevTools();
            }
          },
          { type: 'separator' },
          {
            label: 'Actual Size',
            accelerator: 'CmdOrCtrl+0',
            click: () => {
              this.mainWindow.webContents.setZoomLevel(0);
            }
          },
          {
            label: 'Zoom In',
            accelerator: 'CmdOrCtrl+Plus',
            click: () => {
              const currentZoom = this.mainWindow.webContents.getZoomLevel();
              this.mainWindow.webContents.setZoomLevel(currentZoom + 0.5);
            }
          },
          {
            label: 'Zoom Out',
            accelerator: 'CmdOrCtrl+-',
            click: () => {
              const currentZoom = this.mainWindow.webContents.getZoomLevel();
              this.mainWindow.webContents.setZoomLevel(currentZoom - 0.5);
            }
          }
        ]
      },
      {
        label: 'Navigation',
        submenu: [
          {
            label: 'Learning Paths',
            accelerator: 'Alt+1',
            click: () => this.navigate('/paths')
          },
          {
            label: 'AI Assistant',
            accelerator: 'Alt+2',
            click: () => this.navigate('/assistant')
          },
          {
            label: 'My Progress',
            accelerator: 'Alt+3',
            click: () => this.navigate('/progress')
          }
        ]
      },
      {
        label: 'Help',
        submenu: [
          {
            label: 'Documentation',
            click: () => {
              shell.openExternal('https://docs.nvidia-learning.com');
            }
          },
          {
            label: 'Report Issue',
            click: () => {
              shell.openExternal('https://github.com/nvidia-learning/issues');
            }
          },
          { type: 'separator' },
          {
            label: 'About',
            click: () => this.showAbout()
          }
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  async importProgress() {
    const result = await dialog.showOpenDialog(this.mainWindow, {
      properties: ['openFile'],
      filters: [
        { name: 'JSON Files', extensions: ['json'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (!result.canceled) {
      // Handle import logic
      this.mainWindow.webContents.send('import-progress', result.filePaths[0]);
    }
  }

  async exportProgress() {
    const result = await dialog.showSaveDialog(this.mainWindow, {
      defaultPath: `nvidia-learning-progress-${Date.now()}.json`,
      filters: [
        { name: 'JSON Files', extensions: ['json'] }
      ]
    });

    if (!result.canceled) {
      // Handle export logic
      this.mainWindow.webContents.send('export-progress', result.filePath);
    }
  }

  switchMode(mode) {
    store.set('appMode', mode);

    dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'Mode Changed',
      message: `Application mode changed to ${mode}.`,
      detail: 'Please restart the application for changes to take effect.',
      buttons: ['Restart Now', 'Restart Later']
    }).then(result => {
      if (result.response === 0) {
        app.relaunch();
        app.exit();
      }
    });
  }

  navigate(route) {
    if (this.mainWindow) {
      this.mainWindow.webContents.send('navigate', route);
    }
  }

  openPreferences() {
    // Create preferences window
    const prefsWindow = new BrowserWindow({
      width: 600,
      height: 500,
      parent: this.mainWindow,
      modal: true,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
      }
    });

    prefsWindow.loadFile(path.join(__dirname, 'preferences.html'));
  }

  showAbout() {
    dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'About NVIDIA Learning Platform',
      message: 'NVIDIA Learning Platform',
      detail: `Version: ${app.getVersion()}\n` +
              `Electron: ${process.versions.electron}\n` +
              `Node: ${process.versions.node}\n` +
              `Chrome: ${process.versions.chrome}\n\n` +
              '© 2024 NVIDIA Corporation',
      buttons: ['OK']
    });
  }

  setupAutoUpdater() {
    autoUpdater.checkForUpdatesAndNotify();

    autoUpdater.on('update-available', () => {
      dialog.showMessageBox(this.mainWindow, {
        type: 'info',
        title: 'Update Available',
        message: 'A new version is available. It will be downloaded in the background.',
        buttons: ['OK']
      });
    });

    autoUpdater.on('update-downloaded', () => {
      dialog.showMessageBox(this.mainWindow, {
        type: 'info',
        title: 'Update Ready',
        message: 'Update downloaded. The application will restart to apply the update.',
        buttons: ['Restart Now', 'Later']
      }).then(result => {
        if (result.response === 0) {
          autoUpdater.quitAndInstall();
        }
      });
    });
  }

  checkForUpdates() {
    autoUpdater.checkForUpdatesAndNotify();
  }

  handleAppEvents() {
    app.on('second-instance', () => {
      if (this.mainWindow) {
        if (this.mainWindow.isMinimized()) {
          this.mainWindow.restore();
        }
        this.mainWindow.focus();
      }
    });

    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    app.on('before-quit', () => {
      this.isQuitting = true;

      // Clean up backend process
      if (this.backendProcess) {
        this.backendProcess.kill();
      }
    });
  }
}

// IPC handlers for renderer communication
ipcMain.handle('get-app-mode', () => store.get('appMode'));
ipcMain.handle('get-user-data', () => store.get('userData'));
ipcMain.handle('save-user-data', (event, data) => store.set('userData', data));
ipcMain.handle('get-preferences', () => store.get('preferences'));
ipcMain.handle('save-preferences', (event, prefs) => store.set('preferences', prefs));

// Start the application
const nvidiaApp = new NvidiaLearningDesktop();
nvidiaApp.init();