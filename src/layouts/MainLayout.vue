<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title> Quasar App </q-toolbar-title>

        <div>Quasar v{{ $q.version }}</div>
        <q-space />

        <q-btn dense flat icon="minimize" @click="handleMinimize" />
        <q-btn dense flat icon="crop_square" @click="handleToggleMaximize" />
        <q-btn dense flat icon="close" @click="handleCloseApp" />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header> Essential Links </q-item-label>

        <EssentialLink v-for="link in linksList" :key="link.title" v-bind="link" />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import EssentialLink, { EssentialLinkProps } from 'components/EssentialLink.vue'
import { ref } from 'vue'

defineOptions({
  name: 'MainLayout'
})

const linksList: EssentialLinkProps[] = [
  {
    title: 'Docs',
    caption: 'quasar.dev',
    link: 'https://quasar.dev'
  },
  {
    title: 'Github',
    caption: 'github.com/quasarframework',
    link: 'https://github.com/quasarframework'
  },
  {
    title: 'Discord Chat Channel',
    caption: 'chat.quasar.dev',
    link: 'https://chat.quasar.dev'
  },
  {
    title: 'Forum',
    caption: 'forum.quasar.dev',
    link: 'https://forum.quasar.dev'
  },
  {
    title: 'Twitter',
    caption: '@quasarframework',
    link: 'https://twitter.quasar.dev'
  },
  {
    title: 'Facebook',
    caption: '@QuasarFramework',
    link: 'https://facebook.quasar.dev'
  },
  {
    title: 'Quasar Awesome',
    caption: 'Community Quasar projects',
    link: 'https://awesome.quasar.dev'
  }
]

const leftDrawerOpen = ref(false)

const toggleLeftDrawer = () => {
  leftDrawerOpen.value = !leftDrawerOpen.value
}
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
