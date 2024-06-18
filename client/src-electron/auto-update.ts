import electronUpdater, { UpdateCheckResult } from 'electron-updater'
import { BrowserWindow } from 'electron'
import { logger } from 'app/src-electron/utils.js'

const updateUrl = 'http://192.168.68.225:15244/d/files/%E8%BD%AF%E4%BB%B6%E5%8C%85/data-toolkit'
const {
  autoUpdater,
  CancellationToken
} = electronUpdater

const cancelToken = new CancellationToken()

let mainWindow: BrowserWindow | undefined
autoUpdater.logger = logger
autoUpdater.forceDevUpdateConfig = true
autoUpdater.autoDownload = false
autoUpdater.setFeedURL(updateUrl)

autoUpdater.on('error', (error: Error) => {
  logger.error('Auto updater error:', error)
})

autoUpdater.on('download-progress', (info) => {
  logger.info(`download-progress ${info.percent}%`)
  console.log('download-progress ')
  mainWindow?.webContents.send('updateProgress', info)
})

autoUpdater.on('update-downloaded', (info) => {
  logger.info('update-downloaded')
  logger.info(info)
})

export const setWindow = (win: BrowserWindow | undefined) => {
  mainWindow = win
}

export const checkUpdate = async (win: BrowserWindow | undefined): Promise<UpdateCheckResult | null> => {
  mainWindow = win
  autoUpdater.netSession.setCertificateVerifyProc((_, callback) => {
    // eslint-disable-next-line n/no-callback-literal
    callback(0)
  })
  return await autoUpdater.checkForUpdates()
}

export const downloadUpdate = async (win: BrowserWindow | undefined) => {
  mainWindow = win
  autoUpdater.netSession.setCertificateVerifyProc((_, callback) => {
    // eslint-disable-next-line n/no-callback-literal
    callback(0)
  })
  logger.info('Start update...')
  try {
    void autoUpdater.downloadUpdate(cancelToken)
  } catch (e) {
    logger.error('update Error...', e)
  }
}

export const installUpdateApp = () => {
  autoUpdater.quitAndInstall()
}

export const cancelDownload = () => {
  cancelToken.cancel()
}
