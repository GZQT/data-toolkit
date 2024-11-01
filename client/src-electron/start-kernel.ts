import cp, { ChildProcess } from 'child_process'
import { app, BrowserWindow, net } from 'electron'
import fs from 'fs'
import path from 'path'
import treeKill from 'tree-kill'
import find from 'find-process'
import { checkPortInUse, confDir, getAvailablePort, logger, sleep } from 'app/src-electron/utils.js'
import { components } from 'src/types/api.js'

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
  logger.info(targetPath)
  return targetPath
}

let kernelProcess: ChildProcess | null = null
let kernelPort = 18764

export const getKernelAvailablePort = async () => {
  const isUse = await checkPortInUse(kernelPort)
  if (!isUse) {
    logger.info(`Default port ${kernelPort} can be use.`)
  } else {
    const portNumber = await getAvailablePort()
    logger.info(`Default port ${kernelPort} already in use, get new port to ${portNumber}`)
    kernelPort = portNumber
  }
  return kernelPort
}

export const getKernelPort = () => kernelPort

export const initKernel = async (win: BrowserWindow | undefined): Promise<string | boolean> => {
  if (process.env.RUN_SERVER !== 'true' && process.env.DEV) {
    logger.info('Init kernel skip.')
    return Promise.resolve(true)
  }
  logger.info(`Init kernel on port ${kernelPort}...`)
  const kernelPath = getResources('application.exe')
  if (!fs.existsSync(kernelPath)) {
    logger.error(`⚠️ Kernel program is missing. ${kernelPath}`)
    return Promise.resolve(`⚠️ Kernel program is missing. ${kernelPath}`)
  }
  kernelProcess = cp.spawn(kernelPath, ['-P', `${kernelPort}`, '-p', path.dirname(path.resolve(kernelPath))], {
    detached: false
  })
  logger.info('Booted kernel process [pid=' + kernelProcess.pid + ', port=' + kernelPort + ']')
  kernelProcess.on('spawn', () => {
    const info = '[Kernel process] Process start'
    logger.info(info)
    win?.webContents?.send('Kernel:logs', info)
  })
  kernelProcess.on('close', (code: number) => {
    const info = `[Kernel process] Exist [pid=${kernelProcess?.pid}, port=${kernelPort}] exited with code [${code}]`
    logger.info(info)
    if (code !== 0) {
      const warn = `[Kernel process error]: kernel exit code ${code}`
      logger.error(warn)
    }
  })
  kernelProcess.on('error', (message) => {
    const info = `[pid=${kernelProcess?.pid}, port=${kernelPort}] error [${message}]`
    logger.error(info)
    win?.webContents?.send('Kernel:logs', info)
  })
  kernelProcess.stdout?.on('data', (data) => {
    const info = `${data.toString('utf8')}]`
    logger.info(info)
    win?.webContents?.send('Kernel:logs', info)
  })
  kernelProcess.stdout?.on('error', (data: string) => {
    const error = `${data}]`
    logger.warn(error)
    win?.webContents?.send('Kernel:logs', error)
  })
  kernelProcess.stderr?.on('data', (data) => {
    const info = `${data.toString('utf8')}]`
    logger.info(info)
    win?.webContents?.send('Kernel:logs', info)
  })
  kernelProcess.stderr?.on('error', (data: string) => {
    const error = `${data}]`
    logger.warn(error)
    win?.webContents?.send('Kernel:logs', error)
  })
  let count = 0
  while (count <= 20) {
    try {
      const apiResult = await net.fetch(`http://localhost:${kernelPort}/health`)
      const apiData: components['schemas']['HealthResponse'] = await apiResult.json()
      if (apiData.status === 'ok') {
        return Promise.resolve(true)
      }
      logger.warn('Get kernel response, but is not ok.', apiData)
      await sleep(1000)
    } catch (e) {
      logger.error('Get kernel health failed: ', count, e)
      await sleep(1000)
    } finally {
      count++
    }
  }
  return Promise.reject(`Get kernel health failed! Retry more than ${count} times.`)
}

export const killKernel = async (): Promise<void> => {
  // see  https://github.com/nodejs/help/issues/4050
  if (kernelProcess && kernelProcess.pid) {
    treeKill(kernelProcess.pid)
  }
  const list = await find('name', 'application.exe')
  for (const process of list) {
    treeKill(process.pid)
  }
}

export const restartKernel = async (win: BrowserWindow | undefined) => {
  await killKernel()
  await initKernel(win)
}
