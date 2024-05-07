<script setup lang="ts">
import createClient from 'openapi-fetch'
import { useInterval } from 'quasar'
import { paths } from 'src/types/api'
import { onMounted, ref } from 'vue'
import SettingDialog from './components/SettingDialog.vue'

const { registerInterval } = useInterval()
const status = ref('yellow')
const settingDialogRef = ref<null | InstanceType<typeof SettingDialog>>(null)

defineOptions({
  name: 'MainLayout'
})

// const leftDrawerOpen = ref(false)

const handleMinimize = () => {
  if (process.env.MODE === 'electron') {
    window.WindowsApi.minimize()
  }
}
const handleToggleMaximize = () => {
  if (process.env.MODE === 'electron') {
    window.WindowsApi.toggleMaximize()
  }
}
const handleCloseApp = () => {
  if (process.env.MODE === 'electron') {
    window.WindowsApi.close()
  }
}

onMounted(() => {
  const client = createClient<paths>({
    baseUrl: 'http://localhost:8080'
  })
  registerInterval(async () => {
    try {
      const { data } = await client.GET('/health')
      if (data?.status === 'ok') {
        status.value = 'green'
      } else {
        status.value = 'red'
        console.error(data)
      }
    } catch (error) {
      console.error(error)
      status.value = 'red'
    }
  }, 10000)
})

const handleOpenSetting = () => {
  settingDialogRef.value?.openDialog()
}
</script>

<template>
  <q-layout view="hHh lpR fFf">
    <q-header elevated>
      <q-bar class="q-electron-drag bg-primary">
        <!-- <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" /> -->
        <img style="width:18px; height: 18px;" alt="logo" src="../assets/logo.png" />

        <div class="q-ml-md">Data Toolkit</div>
        <q-badge rounded :color="status" />
        <q-space />

        <q-btn dense flat icon="settings" @click="handleOpenSetting" />
        <q-btn dense flat icon="minimize" @click="handleMinimize" />
        <q-btn dense flat icon="crop_square" @click="handleToggleMaximize" />
        <q-btn dense flat icon="close" @click="handleCloseApp" />
      </q-bar>
    </q-header>

    <!-- <q-drawer v-model="leftDrawerOpen" show-if-above bordered :width="200">
      <q-list>
        <q-item-label header> Essential Links </q-item-label>

        <EssentialLink v-for="link in linksList" :key="link.title" v-bind="link" />
      </q-list>
    </q-drawer> -->

    <q-page-container>
      <q-page padding>
        <router-view />
        <SettingDialog ref="settingDialogRef" />
      </q-page>
    </q-page-container>
  </q-layout>
</template>
