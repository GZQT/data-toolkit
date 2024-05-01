<template>
  <q-card class="container column no-wrap q-ml-md q-px-md q-py-xs full-height">
    <q-tabs v-model="tab" :align="'left'" dense class="text-primary shadow-2">
      <q-route-tab name="file" label="数据文件" :to="`/task/${route.params.id}/file`" exact />
      <q-route-tab name="table" label="数据表格" :to="`/task/${route.params.id}/table`" exact />
      <q-route-tab name="chart" label="图表" :to="`/task/${route.params.id}/chart`" exact />
    </q-tabs>
    <q-separator class="q-mb-md" />
    <div class="router">
      <router-view />
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const tab = ref('files')

const handleToFile = () => {
  if (route.params.id && route.params.id !== '') {
    router.push({ path: `/task/${route.params.id}/file` })
  }
}

onMounted(handleToFile)

watch(() => route.params.id, handleToFile)

</script>

<style scoped lang="scss">
.router {
  height: 100%;
  overflow: auto;
}
</style>
