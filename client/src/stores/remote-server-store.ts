import { defineStore } from 'pinia'
import { onMounted, ref } from 'vue'
import { healthRemoteClient, updateRemoteClient } from 'boot/request'

export const useRemoteServerStore = defineStore('remote-server', () => {
  const remoteServer = ref<string>()
  const status = ref('yellow')
  const response = ref<string>('')
  const getRemoteServer = async () => {
    const address = await window.ApplicationApi.getRemoteServer()
    remoteServer.value = address
    return address
  }
  const handleUpdateRemoteServer = (address: string) => {
    window.ApplicationApi.setRemoteServer(address)
    remoteServer.value = address
    updateRemoteClient(address)
  }
  const checkHealth = async () => {
    try {
      const { data } = await healthRemoteClient.GET('/health')
      response.value = JSON.stringify(data)
      if (data?.status === 'ok') {
        status.value = 'green'
      } else {
        status.value = 'red'
        console.error(data)
      }
    } catch (e) {
      response.value = JSON.stringify(e)
      status.value = 'red'
    }
  }
  onMounted(async () => {
    await getRemoteServer()
    await checkHealth()
  })
  return {
    remoteServer,
    getRemoteServer,
    handleUpdateRemoteServer,
    checkHealth,
    response,
    status
  }
})
