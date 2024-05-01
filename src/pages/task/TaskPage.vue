<script setup lang="ts">
import { client } from 'src/boot/request'
import { components } from 'src/types/api'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const taskData = ref<components['schemas']['TaskResponse'][]>([])

const handleData = async () => {
  const { data } = await client.GET('/task')
  taskData.value = data ?? []
}

onMounted(async () => {
  await handleData()
})
</script>
<template>
  <q-page class="q-pa-md row no-wrap">
    <q-card style="width: 10rem; min-width: 10rem;">
      <q-list dense padding class="rounded-borders text-primary full-width full-height column">
        <q-item-label header class="row justify-between items-center q-py-sm">
          <div class="text-caption">任务</div>
          <q-icon class="cursor-pointer text-caption" name="add" />
        </q-item-label>
        <q-separator />
        <q-scroll-area class="full-width" style="flex: 1;">
          <template v-if="taskData.length > 0">
            <q-item v-for="item in taskData" class="text-base" :key="item.id" :to="`/task/${item.id}`"
              active-class="active-link text-primary" dense clickable v-ripple>
              <q-item-section class="ellipsis">{{ item.name }}</q-item-section>
              <q-tooltip anchor="top middle" :delay="500">
                {{ item.name }}
              </q-tooltip>
            </q-item>
          </template>
          <template v-else>
            <q-item-label header class="row items-center q-py-sm">
              <div class="text-caption text-grey-4">当前列表为空</div>
            </q-item-label>
          </template>
        </q-scroll-area>
      </q-list>
    </q-card>
    <div v-if="route.params.id && route.params.id !== ''" style="flex: 1;max-height: calc(100vh - 80px)">
      <router-view />
    </div>
    <div v-else style="flex: 1; margin-top: 5rem;"
      class="col flex column full-height full-width justify-center items-center text-grey-5">
      <q-icon class="text-h1" name="credit_score" />
      <div class="text-h6 q-mt-md">
        请在左侧选择一个任务后开始
      </div>
      <div class="text-subtitle">
        Please select one task from left side.
      </div>
    </div>
  </q-page>
</template>

<style scoped lang="scss">
.active-link {
  color: $primary;
  background-color: rgba($color: $primary, $alpha: 0.1);
}

:deep(.q-scrollarea__content) {
  width: 100%;
}
</style>
