/**
 * This file is used specifically for security reasons.
 * Here you can access Nodejs stuff and inject functionality into
 * the renderer thread (accessible there through the "window" object)
 *
 * WARNING!
 * If you import anything from node_modules, then make sure that the package is specified
 * in package.json > dependencies and NOT in devDependencies
 *
 * Example (injects window.myAPI.doAThing() into renderer thread):
 *
 *   import { contextBridge } from 'electron'
 *
 *   contextBridge.exposeInMainWorld('myAPI', {
 *     doAThing: () => {}
 *   })
 *
 * WARNING!
 * If accessing Node functionality (like importing @electron/remote) then in your
 * electron-main.ts you will need to set the following when you instantiate BrowserWindow:
 *
 * mainWindow = new BrowserWindow({
 *   // ...
 *   webPreferences: {
 *     // ...
 *     sandbox: false // <-- to be able to import @electron/remote in preload script
 *   }
 * }
 */
import { BrowserWindow } from '@electron/remote'
import { contextBridge, ipcRenderer } from 'electron'
import fs from 'fs'
import readline from 'readline'

contextBridge.exposeInMainWorld('WindowsApi', {
  minimize: () => {
    BrowserWindow.getFocusedWindow()?.minimize()
  },
  toggleMaximize: () => {
    const win = BrowserWindow.getFocusedWindow()

    if (win?.isMaximized()) {
      win?.unmaximize()
    } else {
      win?.maximize()
    }
  },
  close: () => {
    BrowserWindow.getFocusedWindow()?.close()
  }
})

contextBridge.exposeInMainWorld('KernelApi', {
  start: () => ipcRenderer.invoke('KernelApi:start')
})

contextBridge.exposeInMainWorld('FileApi', {
  getFileCount: async (): Promise<number> => {
    const fileStream = fs.createReadStream('C:\\Users\\zyue\\PycharmProjects\\data-crawl\\data_chart\\pu_an_no_1\\data_dau_pa1_1_通用采集仪\\data_dau_pa1_1_通用采集仪_20240331.csv')
    const rl = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity
    })
    return new Promise((resolve, reject) => {
      let lineCount = 0
      rl.on('line', () => {
        lineCount++
      })

      rl.on('close', () => {
        resolve(lineCount)
      })

      rl.on('error', (error) => {
        reject(error)
      })
    })
  },
  selectFiles: (multiSelections: boolean = true): Promise<string[] | undefined> => {
    return ipcRenderer.invoke('FileApi:selectFiles', multiSelections)
  }
})
