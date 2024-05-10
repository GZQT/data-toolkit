import { enable, initialize } from '@electron/remote/main/index.js'
import { BrowserWindow, app, dialog, ipcMain } from 'electron'
import find from 'find-process'
import os from 'os'
import path from 'path'
import treeKill from 'tree-kill'
import { fileURLToPath } from 'url'
import { initKernel, kernelProcess } from './start-kernel'

// https://quasar.dev/quasar-cli-vite/developing-electron-apps/frameless-electron-window#setting-frameless-window
initialize()
// needed in case process is undefined under Linux
const platform = process.platform || os.platform()

const currentDir = fileURLToPath(new URL('.', import.meta.url))

let mainWindow: BrowserWindow | undefined

const createWindow = () => {
  /**
   * Initial window options
   */
  mainWindow = new BrowserWindow({
    icon: path.resolve(currentDir, 'icons/icon.png'), // tray icon
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

  // net.fetch(getServer() + '/api/system/getNetwork', { method: 'POST' }).then((response) => {
  //   return response.json()
  // }).then((response) => {
  //   setProxy(`${response.data.proxy.scheme}://${response.data.proxy.host}:${response.data.proxy.port}`, mainWindow!.webContents).then(() => {
  //     加载主界面
  //     mainWindow!.loadURL(getServer() + '/stage/build/app/index.html?v=' + new Date().getTime())
  //     console.log('代理设置成功')
  //   })
  // })

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
    mainWindow.loadURL(process.env.APP_URL)
  } else {
    mainWindow.loadFile('index.html')
  }

  if (process.env.DEBUGGING) {
    // if on DEV or Production with debug enabled
    mainWindow.webContents.openDevTools()
  } else {
    // we're on production; no access to devtools pls
    mainWindow.webContents.on('devtools-opened', () => {
      mainWindow?.webContents.closeDevTools()
    })
  }

  mainWindow.on('closed', () => {
    mainWindow = undefined
  })
}

ipcMain.handle('KernelApi:start', async () => {
  return initKernel()
})

ipcMain.handle('FileApi:selectFiles', async (_, multiSelections: boolean = true) => {
  const properties: Array<'openFile' | 'openDirectory' | 'multiSelections' | 'showHiddenFiles' | 'createDirectory' | 'promptToCreate' | 'noResolveAliases' | 'treatPackageAsDirectory' | 'dontAddToRecent'> = ['openFile']
  if (multiSelections) {
    properties.push('multiSelections')
  }
  return dialog.showOpenDialogSync({
    properties,
    filters: [
      { name: 'CSV', extensions: ['csv'] }
    ]
  })
})

app.whenReady().then(createWindow)

app.on('window-all-closed', async () => {
  // see  https://github.com/nodejs/help/issues/4050
  if (kernelProcess && kernelProcess.pid) {
    treeKill(kernelProcess.pid)
  }
  const list = await find('name', 'application.exe')
  for (const process of list) {
    treeKill(process.pid)
  }
  if (platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === undefined) {
    createWindow()
  }
})
