<template>
  <q-page class="row">
    <div @click="handleFile">test</div>
    <div>{{ loading ? 'Loading...' : 'No data' }}</div>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineOptions({
  name: 'IndexPage'
})

const loading = ref(false)

const handleFile = () => {
  loading.value = true
  window.FileApi.getFileCount()
    .then(count => {
      console.log(count)
    })
    .catch((err) => {
      console.log(err)
    })
    .finally(() => {
      loading.value = false
    })
}

</script>
