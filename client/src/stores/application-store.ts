import { defineStore } from 'pinia'
import { date } from 'quasar'
import { healthClient } from 'boot/request'
import { ref } from 'vue'

export const useApplicationStore = defineStore('application', () => {
  const showTime = ref<boolean>(true)
  const status = ref('yellow')
  const time = ref<number>(0)
  const response = ref<string>('')
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
    } finally {
      showTime.value = true
      const end = parseInt(date.formatDate(Date.now(), 'x'))
      time.value = end - start
      setTimeout(() => {
        showTime.value = false
      }, 3000)
    }
  }
  return {
    showTime,
    status,
    time,
    response,
    checkHealth
  }
})
