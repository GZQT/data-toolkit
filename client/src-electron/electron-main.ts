import { enable, initialize } from '@electron/remote/main/index.js'
import { BrowserWindow, app, dialog, ipcMain } from 'electron'
import os from 'os'
import path from 'path'
import { fileURLToPath } from 'url'
import { getKernelAvailablePort, getKernelPort, initKernel, killKernel, restartKernel } from './start-kernel'
import { cancelDownload, checkUpdate, downloadUpdate, installUpdateApp, setWindow } from './auto-update'

// https://quasar.dev/quasar-cli-vite/developing-electron-apps/frameless-electron-window#setting-frameless-window
initialize()
// needed in case process is undefined under Linux
const platform = process.platform || os.platform()

const currentDir = fileURLToPath(new URL('.', import.meta.url))

let mainWindow: BrowserWindow | undefined

const createWindow = () => {
  mainWindow = new BrowserWindow({
    icon: path.resolve(currentDir, 'icons/icon.png'),
    width: 1200,
    height: 720,
    minWidth: 1200,
    minHeight: 480,
    useContentSize: true,
    frame: false,
    webPreferences: {
      sandbox: false,
      contextIsolation: true,
      webSecurity: false,
      // More info: https://v2.quasar.dev/quasar-cli-vite/developing-electron-apps/electron-preload-script
      preload: path.resolve(
        currentDir,
        path.join(process.env.QUASAR_ELECTRON_PRELOAD_FOLDER, 'electron-preload' + process.env.QUASAR_ELECTRON_PRELOAD_EXTENSION)
      )
    }
  })
  enable(mainWindow.webContents)
  mainWindow.webContents.session.setSpellCheckerLanguages(['en-US'])
  mainWindow.webContents.session.webRequest.onBeforeSendHeaders((details, cb) => {
    const header = { requestHeaders: details.requestHeaders }
    for (const key in details.requestHeaders) {
      if (key.toLowerCase() === 'referer') {
        delete details.requestHeaders[key]
      }
    }
    cb(header)
  })
  mainWindow.webContents.session.webRequest.onHeadersReceived((details, cb) => {
    for (const key in details.responseHeaders) {
      if (key.toLowerCase() === 'x-frame-options') {
        delete details.responseHeaders[key]
      } else if (key.toLowerCase() === 'content-security-policy') {
        delete details.responseHeaders[key]
      } else if (key.toLowerCase() === 'access-control-allow-origin') {
        delete details.responseHeaders[key]
      }
    }
    const header = { responseHeaders: details.responseHeaders }
    cb(header)
  })

  if (process.env.DEV) {
    void mainWindow.loadURL(process.env.APP_URL)
  } else {
    void mainWindow.loadFile('index.html')
  }

  if (process.env.DEBUGGING) {
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.webContents.on('devtools-opened', () => {
      // mainWindow?.webContents.closeDevTools()
    })
  }

  mainWindow.on('closed', () => {
    mainWindow = undefined
  })
  setWindow(mainWindow)
}

ipcMain.handle('KernelApi:start', initKernel)
ipcMain.handle('KernelApi:restartKernel', restartKernel)
ipcMain.handle('KernelApi:getKernelPort', () => getKernelPort())
ipcMain.handle('KernelApi:getKernelAvailablePort', () => getKernelAvailablePort())
ipcMain.handle('FileApi:getExeDirectory', () => app.getPath('exe'))

ipcMain.handle('FileApi:selectFiles', async (_, multiSelections: boolean = true) => {
  const properties: Array<'openFile' | 'openDirectory' | 'multiSelections' | 'showHiddenFiles' | 'createDirectory' | 'promptToCreate' |
    'noResolveAliases' | 'treatPackageAsDirectory' | 'dontAddToRecent'> = ['openFile']
  if (multiSelections) {
    properties.push('multiSelections')
  }
  return dialog.showOpenDialogSync({
    properties,
    filters: [{
      name: 'CSV',
      extensions: ['csv']
    }]
  })
})

ipcMain.handle('ApplicationApi:checkUpdate', () => checkUpdate(mainWindow))
ipcMain.handle('ApplicationApi:downloadUpdate', () => downloadUpdate(mainWindow))
ipcMain.handle('ApplicationApi:installUpdateApp', async () => {
  await killKernel()
  installUpdateApp()
})

app.whenReady()
  .then(createWindow)

app.on('window-all-closed', async () => {
  cancelDownload()
  await killKernel()
  if (platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === undefined) {
    createWindow()
  }
})

const gotTheLock = app.requestSingleInstanceLock()
if (!gotTheLock) {
  app.quit()
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore()
      mainWindow.focus()
    }
  })
}
