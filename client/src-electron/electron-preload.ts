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
import { contextBridge, FileFilter, ipcRenderer, shell } from 'electron'
import fs from 'fs'
import os from 'os'
import path from 'path'
import readline from 'readline'
import { ProgressInfo } from 'electron-updater'
import { Report } from 'pages/report/report-store'

const getAllFiles = (dirPath: string, arrayOfFiles: string[] = []): string[] => {
  if (!fs.existsSync(dirPath)) {
    return []
  }
  const files = fs.readdirSync(dirPath)
  files.forEach(file => {
    const filePath = path.join(dirPath, file)
    if (fs.statSync(filePath).isDirectory()) {
      arrayOfFiles = getAllFiles(filePath, arrayOfFiles)
    } else {
      arrayOfFiles.push(filePath)
    }
  })
  return arrayOfFiles
}

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
  start: () => ipcRenderer.invoke('KernelApi:start'),
  getKernelPort: () => ipcRenderer.invoke('KernelApi:getKernelPort'),
  getKernelAvailablePort: () => ipcRenderer.invoke('KernelApi:getKernelAvailablePort'),
  restartKernel: () => ipcRenderer.invoke('KernelApi:restartKernel')
})

contextBridge.exposeInMainWorld('ReportApi', {
  generate: (report: Report): Promise<void> => ipcRenderer.invoke('ReportApi:generate', report)
})

contextBridge.exposeInMainWorld('ApplicationApi', {
  onUpdateProgress: (func: (info: ProgressInfo) => void) => {
    ipcRenderer.on('updateProgress', (_, info) => func(info))
  },
  checkUpdate: () => ipcRenderer.invoke('ApplicationApi:checkUpdate'),
  downloadUpdate: () => ipcRenderer.invoke('ApplicationApi:downloadUpdate'),
  installUpdateApp: () => ipcRenderer.invoke('ApplicationApi:installUpdateApp'),
  getRemoteServer: () => ipcRenderer.invoke('ApplicationApi:getRemoteServer'),
  setRemoteServer: (address: string) => ipcRenderer.invoke('ApplicationApi:setRemoteServer', address)
})

contextBridge.exposeInMainWorld('FileApi', {
  getFileCount: async (file: string): Promise<{ total: number, updatedDate?: Date }> => {
    if (!fs.existsSync(file)) {
      return { total: -1 }
    }
    const fileStat = fs.statSync(file)
    const fileStream = fs.createReadStream(file)
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
        resolve({
          total: lineCount,
          updatedDate: fileStat.mtime
        })
      })

      rl.on('error', (error) => {
        reject(error)
      })
    })
  },
  selectFiles: (multiSelections: boolean = true,
    openDirectory: boolean = false,
    filters: FileFilter[] = [{
      name: 'CSV',
      extensions: ['csv']
    }]): Promise<string[] | undefined> => {
    return ipcRenderer.invoke('FileApi:selectFiles', multiSelections, openDirectory, filters)
  },
  checkExistPath: (file: string): boolean => {
    return fs.existsSync(file)
  },
  openFileDirectory: (file: string) => {
    if (fs.existsSync(file)) {
      shell.showItemInFolder(file)
    }
  },
  openDirectory: (dirPath: string) => {
    if (fs.existsSync(dirPath)) {
      void shell.openPath(dirPath)
    }
  },
  openExeDirectory: async () => {
    const appPath = await ipcRenderer.invoke('FileApi:getExeDirectory')
    shell.showItemInFolder(appPath)
  },
  openApplicationDirectory: async (dirname: string) => {
    const homeDirectory = os.homedir()
    const abs = path.join(homeDirectory, 'data-toolkit', dirname)
    if (fs.existsSync(abs)) {
      await shell.openPath(path.join(homeDirectory, 'data-toolkit', dirname))
    } else {
      await shell.openPath(path.join(homeDirectory, 'data-toolkit'))
    }
  },
  getCsvHeader: async (file: string) => {
    return new Promise((resolve, reject) => {
      if (!fs.existsSync(file)) {
        resolve([])
        return
      }
      const fileStream = fs.createReadStream(file)
      const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
      })
      let lines: string[] = []
      let lineCount = 0
      rl.on('line', (line: string) => {
        if (lineCount === 0) {
          lines = line.split(',').filter(item => item !== '')
            .map(item => item.replaceAll('\'', '').replaceAll('"', ''))
          resolve(lines)
        }
        lineCount++
        fileStream.close()
      })
      rl.on('error', (error) => {
        reject(error)
      })
    })
  },
  getApplicationDirectoryFiles: (dirname: string): string[] => {
    const homeDirectory = os.homedir()
    const abs = path.join(homeDirectory, 'data-toolkit', dirname)
    return getAllFiles(abs)
  },
  openExternalLink: (url: string) => {
    void shell.openExternal(url)
  }
})
