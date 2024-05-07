<template>
  <q-layout view="hHh lpR fFf">
    <q-header elevated>
      <q-bar class="q-electron-drag bg-primary">
        <!-- <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" /> -->
        <img style="width:18px; height: 18px;" alt="logo" src="../assets/logo.png" />

        <div class="q-ml-md">Data Toolkit</div>
        <q-space />

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
      </q-page>

      <q-page-scroller position="bottom-right" :scroll-offset="150" :offset="[18, 18]">
        <q-btn fab icon="keyboard_arrow_up" color="accent" />
      </q-page-scroller>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
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
</script>
