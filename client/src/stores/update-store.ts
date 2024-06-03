import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import { QNotifyUpdateOptions } from 'quasar/dist/types/api'
import { ProgressInfo, UpdateCheckResult, UpdateInfo } from 'electron-updater'
import { useQuasar } from 'quasar'

export const useUpdateStore = defineStore('update', () => {
  const $q = useQuasar()
  const data = reactive({
    loading: false,
    hasNewVersion: false,
    version: process.env.APPLICATION_VERSION,
    newVersion: process.env.APPLICATION_VERSION,
    progress: 0
  })
  const downloadProgress = ref<((props?: QNotifyUpdateOptions) => void) | null>(null)
  const newVersionIsDownloading = ref(false)
  const updateDownloading = (status: boolean) => {
    newVersionIsDownloading.value = status
  }

  const handleDownloadEvent = () => {
    window.ApplicationApi.onUpdateProgress((info: ProgressInfo) => {
      console.log(info)
      if (downloadProgress.value === null) {
        return
      }
      downloadProgress.value({
        caption: `${info.percent.toFixed(2)}% ${(info.bytesPerSecond / (1024 * 1024)).toFixed(2)}MB/s`
      })
      if (info.percent === 100) {
        newVersionIsDownloading.value = false
        downloadProgress.value({
          icon: 'done',
          spinner: false,
          message: '下载完成！',
          timeout: 0,
          actions: [{
            label: '立即安装',
            color: 'primary',
            size: 'md',
            dense: true,
            handler: () => {
              window.ApplicationApi.installUpdateApp()
            }
          }]
        })
      }
    })
  }

  const handleCheckUpdate = async (noNewNotify: boolean = false) => {
    if (downloadProgress.value !== null) {
      return
    }
    data.loading = true
    let result: UpdateCheckResult | null = null
    try {
      result = await window.ApplicationApi.checkUpdate()
    } catch (e) {
      $q.notify({
        type: 'warning',
        message: `检查更新失败，${e}`
      })
      return
    } finally {
      data.loading = false
    }
    if (result === null) {
      $q.notify({
        type: 'warning',
        message: '检查更新失败，未获取到新版本信息'
      })
      return
    }
    const updateInfo: UpdateInfo = result.updateInfo
    const hasNewVersion = updateInfo.version !== data.version
    data.hasNewVersion = hasNewVersion
    if (!hasNewVersion) {
      if (noNewNotify) {
        $q.notify({
          type: 'info',
          message: '当前已经是最新版本了'
        })
      }
      return
    }
    data.newVersion = updateInfo.version
    $q.notify({
      icon: 'info',
      message: `存在新版本 ${data.newVersion}, 当前版本 ${data.version}。`,
      actions: [
        {
          label: '现在更新',
          color: 'primary',
          size: 'md',
          dense: true,
          handler: () => {
            window.ApplicationApi.downloadUpdate()
            newVersionIsDownloading.value = true
            downloadProgress.value = $q.notify({
              group: false,
              timeout: 0,
              spinner: true,
              message: '正在下载...',
              caption: '0%'
            })
          }
        },
        {
          label: '忽略',
          color: 'primary',
          size: 'md'
        }
      ]
    })
  }

  return {
    newVersionIsDownloading,
    data,
    handleDownloadEvent,
    updateDownloading,
    handleCheckUpdate
  }
})
