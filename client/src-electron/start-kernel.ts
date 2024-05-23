import cp, { ChildProcess } from 'child_process'
import { app, net } from 'electron'
import fs from 'fs'
import path from 'path'
import { checkPortInUse, confDir, getAvailablePort, logger, sleep } from './utils'
import { components } from 'src/types/api'

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
  return Promise.resolve(kernelPort)
}

export const getKernelPort = () => kernelPort

export const initKernel = async (): Promise<string | boolean> => {
  if (process.env.RUN_SERVER !== 'true') {
    logger.info('Init kernel skip.')
    return Promise.resolve(true)
  }
  logger.info('Init kernel...')
  const kernelPath = getResources('application.exe')
  if (!fs.existsSync(kernelPath)) {
    logger.error(`⚠️ Kernel program is missing. ${kernelPath}`)
    return Promise.resolve(`⚠️ Kernel program is missing. ${kernelPath}`)
  }
  kernelProcess = cp.spawn(kernelPath, [], {
    stdio: 'ignore',
    detached: false
  })
  logger.info('Booted kernel process [pid=' + kernelProcess.pid + ', port=' + kernelPort + ']')
  kernelProcess.on('close', (code: number) => {
    logger.info(`kernel [pid=${kernelProcess?.pid}, port=${kernelPort}] exited with code [${code}]`)
    if (code !== 0) {
      logger.error(`Error: kernel exit code ${code}`)
    }
  })
  let count = 0
  while (count <= 20) {
    try {
      net.fetch(`http://localhost:${kernelPort}/health`).then()
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
export { kernelProcess }
