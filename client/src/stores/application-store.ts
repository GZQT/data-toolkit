import { defineStore } from 'pinia'
import { date } from 'quasar'
import { healthClient } from 'boot/request'
import { onMounted, ref } from 'vue'

export const useApplicationStore = defineStore('application', () => {
  const showTime = ref<boolean>(true)
  const status = ref('yellow')
  const time = ref<number>(0)
  const response = ref<string>('')
  const errorCount = ref(0)
  const logs = ref<string[]>([])

  const autoToBottom = ref(true)
  const isRunning = ref(true)
  const checkHealth = async () => {
    const start = parseInt(date.formatDate(Date.now(), 'x'))
    try {
      const { data } = await healthClient.GET('/health')
      response.value = JSON.stringify(data)
      if (data?.status === 'ok') {
        status.value = 'green'
      } else {
        status.value = 'red'
        console.error(data)
      }
    } catch (error) {
      console.error(error)
      status.value = 'red'
      errorCount.value += 1
    } finally {
      showTime.value = true
      const end = parseInt(date.formatDate(Date.now(), 'x'))
      time.value = end - start
      setTimeout(() => {
        showTime.value = false
      }, 3000)
      if (errorCount.value > 100) {
        errorCount.value = 0
        console.log('内核健康检测失败超过 100 次，尝试重启内核')
        const result = await window.KernelApi.start()
        if (result === true) {
          console.log('内核重启成功')
        } else {
          console.log('内核重启失败')
        }
      }
    }
  }

  onMounted(() => {
    window?.KernelApi.registerLogsInformation((info) => {
      logs.value.push(info)
      isRunning.value = !info.startsWith('[Kernel process] Exist')
    })
  })
  return {
    showTime,
    status,
    time,
    response,
    logs,
    autoToBottom,
    isRunning,
    checkHealth
  }
})
