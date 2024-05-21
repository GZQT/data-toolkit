import cp, { ChildProcess } from 'child_process'
import { app } from 'electron'
import fs from 'fs'
import path from 'path'

const localServer = 'http://127.0.0.1'
const confDir = path.join(app.getPath('home'), '.config', 'data-toolkit')
const kernelPort = 18764
const appDir = path.dirname(app.getAppPath())
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

let kernelProcess: ChildProcess | null = null

export const initKernel = () => {
  if (process.env.RUN_SERVER === 'true' || !process.env.DEV) {
    writeLog('Init kernel...')
    const kernelPath = getResources('application.exe')
    if (!fs.existsSync(kernelPath)) {
      return `⚠️ 内核程序丢失 Kernel program is missing. ${kernelPath}`
    }
    kernelProcess = cp.spawn(kernelPath, [], {
      stdio: 'ignore',
      detached: false
    })
    writeLog('booted kernel process [pid=' + kernelProcess.pid + ', port=' + kernelPort + ']')
    const currentKernelPort = kernelPort
    kernelProcess.on('close', (code: number) => {
      writeLog(`kernel [pid=${kernelProcess?.pid}, port=${currentKernelPort}] exited with code [${code}]`)
      if (code !== 0) {
        writeLog(`Error: kernel exit code ${code}`)
      }
    })
  } else {
    writeLog('Init kernel skip.')
  }
  return true
}
export {
  kernelProcess
}
