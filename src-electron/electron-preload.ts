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
import { contextBridge, ipcRenderer, shell } from 'electron'
import fs from 'fs'
import os from 'os'
import path from 'path'
import readline from 'readline'

const countFiles = async (dir: string, inApplication = true): Promise<number> => {
  let targetDir = dir
  if (inApplication) {
    targetDir = path.join(os.homedir(), 'data-toolkit', dir)
  }
  let totalFiles = 0

  if (!fs.existsSync(targetDir)) {
    return Promise.resolve(0)
  }

  // 读取文件夹内容
  const items = await fs.promises.readdir(targetDir, { withFileTypes: true })

  // 使用 Promise.all 并行处理所有项
  const counts = await Promise.all(items.map(item => {
    const fullPath = path.join(dir, item.name)
    return item.isDirectory() ? countFiles(fullPath, inApplication) : 1
  }))

  // 累加所有返回的计数
  totalFiles = counts.reduce((acc, num) => acc + num, 0)

  return totalFiles
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
  start: () => ipcRenderer.invoke('KernelApi:start')
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
  selectFiles: (multiSelections: boolean = true): Promise<string[] | undefined> => {
    return ipcRenderer.invoke('FileApi:selectFiles', multiSelections)
  },
  openFileDirectory: (file: string) => {
    if (fs.existsSync(file)) {
      shell.showItemInFolder(file)
    }
  },
  openApplicationDirectory: async (dirname: string) => {
    const homeDirectory = os.homedir()
    const abs = path.join(homeDirectory, 'data-toolkit', dirname)
    if (fs.existsSync(abs)) {
      await shell.openPath(abs)
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
  countFiles,
  openExternalLink: (url: string) => {
    shell.openExternal(url)
  }
})
