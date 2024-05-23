import electronUpdater, { UpdateCheckResult } from 'electron-updater'
import log from 'electron-log'
import { BrowserWindow } from 'electron'
import { logger } from 'app/src-electron/utils'

const updateUrl = 'https://36.134.229.254:5244/d/dist/data-toolkit'
const { autoUpdater, CancellationToken } = electronUpdater
autoUpdater.logger = log
autoUpdater.forceDevUpdateConfig = true
autoUpdater.autoDownload = false
autoUpdater.setFeedURL(updateUrl)

const cancelToken = new CancellationToken()
let mainWindow: BrowserWindow | undefined

export const setWindow = (win: BrowserWindow | undefined) => {
  mainWindow = win
}

// 注册更新过程中的各种事件
autoUpdater.on('error', (error: Error) => {
  logger.error('Auto updater error:', error)
})

autoUpdater.on('download-progress', (info) => {
  log.info(`download-progress ${info.percent}%`)
  mainWindow?.webContents.send('updateProgress', info)
})

autoUpdater.on('update-downloaded', (info) => {
  log.info('update-downloaded')
  log.info(info)
})

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
  void autoUpdater.downloadUpdate(cancelToken)
}

export const installUpdateApp = () => {
  autoUpdater.quitAndInstall()
}

export const cancelDownload = () => {
  cancelToken.cancel()
}
