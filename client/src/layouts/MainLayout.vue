<script setup lang="ts">
import { useInterval, useQuasar } from 'quasar'
import Logo from 'src/assets/logo.png'
import { onMounted } from 'vue'
import SettingDialog from './components/SettingDialog.vue'
import { isElectron } from 'src/utils/action'
import { useUpdateStore } from 'stores/update-store'
import { useApplicationStore } from 'stores/application-store'

const { registerInterval } = useInterval()
const $q = useQuasar()
defineOptions({
  name: 'MainLayout'
})
const updateStore = useUpdateStore()
const applicationStore = useApplicationStore()
const handleMinimize = () => {
  if (isElectron()) {
    window.WindowsApi.minimize()
  }
}
const handleToggleMaximize = () => {
  if (isElectron()) {
    window.WindowsApi.toggleMaximize()
  }
}
const handleCloseApp = () => {
  if (isElectron()) {
    window.WindowsApi.close()
  }
}

onMounted(() => {
  applicationStore.checkHealth()
  registerInterval(applicationStore.checkHealth, 10000)
  updateStore.handleCheckUpdate()
})

const handleOpenSetting = () => {
  $q.dialog({ component: SettingDialog })
}
</script>

<template>
  <q-layout view="hHh lpR fFf">
    <q-header elevated>
      <q-bar class="q-electron-drag bg-primary">
        <!-- <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" /> -->
        <img style="width:18px; height: 18px;" alt="logo" :src="Logo" />

        <div class="q-ml-md">Data Toolkit</div>
        <q-badge rounded :color="applicationStore.status" style="transition: all 1s;" />
        <q-space />

        <q-btn dense flat icon="settings" @click="handleOpenSetting">
          <q-badge v-show="updateStore.data.hasNewVersion" floating color="red" rounded></q-badge>
        </q-btn>
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
        <div v-if="applicationStore.time > 0" class="text-caption fixed bg-grey-7 text-white q-px-sm"
          :style="{ bottom: 0, left: 0, opacity: applicationStore.showTime ? 0.5 : 0, transition: 'all 1s' }">
          {{ applicationStore.time }}ms
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>
