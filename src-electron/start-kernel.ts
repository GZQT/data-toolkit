import cp, { ChildProcess } from 'child_process'
import { BrowserWindow, WebContents, app, screen } from 'electron'
import fs from 'fs'
import path from 'path'

const localServer = 'http://127.0.0.1'
const confDir = path.join(app.getPath('home'), '.config', 'data-toolkit')
const kernelPort = 8080
const appDir = path.dirname(app.getAppPath())
const appVer = app.getVersion()
if (!fs.existsSync(confDir)) {
  fs.mkdirSync(confDir, { recursive: true })
}

const getResources = (file: string) => {
  let targetPath = path.join(appDir, 'appearance', file)
  if (process.env.DEV) {
    // dev 下不会将内容打包到运行目录下，运行目录为 .quasar，需要取到项目根目录后获取
    const projectDir = path.dirname(appDir)
    targetPath = path.join(projectDir, 'src-electron', file)
  }
  return targetPath
}

export const getServer = (port = kernelPort) => {
  return localServer + ':' + port
}
export const writeLog = (out: string) => {
  console.log(out)
  const logFile = path.join(confDir, 'app.log')
  let log = ''
  const maxLogLines = 1024
  try {
    if (fs.existsSync(logFile)) {
      log = fs.readFileSync(logFile).toString()
      const lines = log.split('\n')
      if (maxLogLines < lines.length) {
        log = lines.slice(maxLogLines / 2, maxLogLines).join('\n') + '\n'
      }
    }
    out = out.toString()
    out = new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '') + ' ' + out
    log += out + '\n'
    fs.writeFileSync(logFile, log)
  } catch (e) {
    console.error(e)
  }
}

export const setProxy = (proxyURL: string, webContents: WebContents) => {
  if (proxyURL.startsWith('://')) {
    console.log('network proxy [system]')
    return webContents.session.setProxy({ mode: 'system' })
  }
  console.log('network proxy [' + proxyURL + ']')
  return webContents.session.setProxy({ proxyRules: proxyURL })
}

const showErrorWindow = (title: string, content: string): number => {
  const errorHTMLPath = getResources('error.html')
  const errWindow = new BrowserWindow({
    width: Math.floor(screen.getPrimaryDisplay().size.width * 0.5),
    height: Math.floor(screen.getPrimaryDisplay().workAreaSize.height * 0.8),
    frame: false,
    icon: path.join(appDir, 'stage', 'icon-large.png'),
    webPreferences: {
      nodeIntegration: true, webviewTag: true, webSecurity: false, contextIsolation: false
    }
  })
  errWindow.loadFile(errorHTMLPath, {
    query: {
      home: app.getPath('home'),
      v: appVer,
      title,
      content,
      icon: path.join(appDir, 'stage', 'icon-large.png')
    }
  })
  errWindow.show()
  return errWindow.id
}

let bootWindow: BrowserWindow

const exitApp = (port: number, errorWindowId?: number) => {
  if (errorWindowId) {
    BrowserWindow.getAllWindows().forEach((item) => {
      if (errorWindowId !== item.id) {
        item.destroy()
      }
    })
  } else {
    app.exit()
  }
}
let kernelProcess: ChildProcess | null = null
export const initKernel = (port: number) => {
  return new Promise((resolve, reject) => {
    bootWindow = new BrowserWindow({
      width: Math.floor(screen.getPrimaryDisplay().size.width / 2),
      height: Math.floor(screen.getPrimaryDisplay().workAreaSize.height / 2),
      frame: false,
      backgroundColor: '#1e1e1e',
      webPreferences: {
        devTools: true
      }
    })
    console.log(port)

    const targetPath = getResources('boot.html')
    bootWindow.loadFile(targetPath, { query: { v: appVer } })
    bootWindow.show()
    console.log(process.env.RUN_SERVER, process.env.RUN_SERVER === 'true')

    if (process.env.RUN_SERVER === 'true' || !process.env.DEV) {
      const kernelPath = getResources('application.exe')
      if (!fs.existsSync(kernelPath)) {
        showErrorWindow('⚠️ 内核程序丢失 Kernel program is missing', `<div>内核程序丢失。</div><div>The kernel program is not found.</div><div><i>${kernelPath}</i></div>`)
        bootWindow.destroy()
        reject('Can not find kernel path.')
        return
      }
      kernelProcess = cp.spawn(kernelPath, [], {
        stdio: 'ignore',
        detached: true
      })
      writeLog('booted kernel process [pid=' + kernelProcess.pid + ', port=' + kernelPort + ']')
      const currentKernelPort = kernelPort
      kernelProcess.on('close', (code: number) => {
        writeLog(`kernel [pid=${kernelProcess?.pid}, port=${currentKernelPort}] exited with code [${code}]`)
        if (code !== 0) {
          let errorWindowId
          switch (code) {
            case 20:
              errorWindowId = showErrorWindow('⚠️ 数据库被锁定 The database is locked', '<div>数据库文件正在被其他进程占用，请检查是否同时存在多个内核进程（SiYuan Kernel）服务相同的工作空间。</div><div>The database file is being occupied by other processes, please check whether there are multiple kernel processes (SiYuan Kernel) serving the same workspace at the same time.</div>')
              break
            case 21:
              errorWindowId = showErrorWindow('⚠️ 监听端口 ' + currentKernelPort + ' 失败 Failed to listen to port ' + currentKernelPort, '<div>监听 ' + currentKernelPort + ' 端口失败，请确保程序拥有网络权限并不受防火墙和杀毒软件阻止。</div><div>Failed to listen to port ' + currentKernelPort + ', please make sure the program has network permissions and is not blocked by firewalls and antivirus software.</div>')
              break
            case 24:
              errorWindowId = showErrorWindow('⚠️ 工作空间已被锁定 The workspace is locked', '<div>该工作空间正在被使用，请尝试在任务管理器中结束 SiYuan-Kernel 进程或者重启操作系统后再启动思源。</div><div>The workspace is being used, please try to end the SiYuan-Kernel process in the task manager or restart the operating system and then start SiYuan.</div>')
              break
            case 25:
              errorWindowId = showErrorWindow('⚠️ 初始化工作空间失败 Failed to create workspace directory', '<div>初始化工作空间失败。</div><div>Failed to init workspace.</div>')
              break
            case 26:
              errorWindowId = showErrorWindow('🚒 已成功避免潜在的数据损坏<br>Successfully avoid potential data corruption', '<div>工作空间下的文件正在被第三方软件（比如同步盘 iCloud/OneDrive/Dropbox/Google Drive/坚果云/百度网盘/腾讯微云等）扫描读取占用，继续使用会导致数据损坏，思源内核已经安全退出。<br><br>请将工作空间移动到其他路径后再打开，停止同步盘同步工作空间。如果以上步骤无法解决问题，请参考<a href="https://ld246.com/article/1684586140917">这里</a>或者<a href="https://ld246.com/article/1649901726096" target="_blank">发帖</a>寻求帮助。</div><hr><div>The files in the workspace are being scanned and read by third-party software (such as sync disk iCloud/OneDrive/Dropbox/Google Drive/Nutstore/Baidu Netdisk/Tencent Weiyun, etc.), continuing to use it will cause data corruption, and the SiYuan kernel is already safe shutdown.<br><br>Move the workspace to another path and open it again, stop the sync disk to sync the workspace. If the above steps do not resolve the issue, please look for help or report bugs <a href="https://liuyun.io/article/1686530886208" target="_blank">here</a>.</div>')
              break
            case 0:
              break
            default:
              errorWindowId = showErrorWindow('⚠️ 内核因未知原因退出 The kernel exited for unknown reasons', `<div>内核因未知原因退出 [code=${code}]，请尝试重启操作系统后再启动。如果该问题依然发生，请检查杀毒软件是否阻止思源内核启动。</div><div>SiYuan Kernel exited for unknown reasons [code=${code}], please try to reboot your operating system and then start SiYuan again. If occurs this problem still, please check your anti-virus software whether kill the SiYuan Kernel.</div>`)
              break
          }
          exitApp(currentKernelPort, errorWindowId)
          bootWindow?.destroy()
          writeLog(`Error: kernel exit code ${code} ${errorWindowId}`)
        }
      })
    }
    resolve(true)
  })
}
export {
  kernelProcess
}
