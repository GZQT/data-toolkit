import cp, { ChildProcess } from 'child_process'
import { app } from 'electron'
import fs from 'fs'
import path from 'path'
import { confDir, logger } from './utils'

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

let kernelProcess: ChildProcess | null = null

export const initKernel = () => {
  if (process.env.RUN_SERVER === 'true' || !process.env.DEV) {
    logger.info('Init kernel...')
    const kernelPath = getResources('application.exe')
    if (!fs.existsSync(kernelPath)) {
      logger.error(`⚠️ Kernel program is missing. ${kernelPath}`)
      return `⚠️ Kernel program is missing. ${kernelPath}`
    }
    kernelProcess = cp.spawn(kernelPath, [], { stdio: 'ignore', detached: false })
    logger.info('booted kernel process [pid=' + kernelProcess.pid + ', port=' + kernelPort + ']')
    const currentKernelPort = kernelPort
    kernelProcess.on('close', (code: number) => {
      logger.info(`kernel [pid=${kernelProcess?.pid}, port=${currentKernelPort}] exited with code [${code}]`)
      if (code !== 0) {
        logger.error(`Error: kernel exit code ${code}`)
      }
    })
  } else {
    logger.info('Init kernel skip.')
  }
  return true
}
export { kernelProcess }
