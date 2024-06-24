<script setup lang="ts">
import { useQuasar } from 'quasar'
import { client } from 'src/boot/request'
import { components } from 'src/types/api'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const tab = ref('generator')
const $q = useQuasar()
const router = useRouter()
const taskData = ref<components['schemas']['TaskResponse'][]>([])

const handleData = async () => {
  const { data } = await client.GET('/task')
  taskData.value = data ?? []
}

const handleAddTask = () => {
  $q.dialog({
    title: '添加任务',
    message: '请输入任务名称',
    prompt: {
      model: '',
      type: 'text'
    },
    cancel: true
  }).onOk(async (data) => {
    await client.POST('/task', {
      body: { name: data }
    })
    await handleData()
    if (taskData.value.length > 0) {
      void router.push(`/generator/${taskData.value[0].id}`)
      tab.value = `chart-${taskData.value[0].id}`
    }
  })
}

onMounted(async () => {
  await handleData()
  if (taskData.value.length > 0) {
    void router.push(`/generator/${taskData.value[0].id}`)
    tab.value = `chart-${taskData.value[0].id}`
  }
})

const handleRename = async (item: components['schemas']['TaskResponse']) => {
  $q.dialog({
    title: '编辑任务',
    message: '请输入任务名称',
    prompt: {
      model: item.name,
      type: 'text'
    },
    cancel: true
  }).onOk(async (data) => {
    await client.PUT('/task/{task_id}', {
      params: {
        path: { task_id: item.id }
      },
      body: { name: data }
    })
    await handleData()
  })
}

const handleDelete = async (item: components['schemas']['TaskResponse']) => {
  $q.dialog({
    title: '确认删除',
    message: `你确认删除 ${item.name} 吗？<div class="text-weight-bolder text-red">注：此操作不可逆，与之关联的数据都会被删除，已生成的图表不会删除</div>`,
    cancel: {
      color: 'primary',
      outline: true
    },
    ok: {
      color: 'negative',
      outline: true
    },
    html: true,
    focus: 'cancel'
  }).onOk(async () => {
    await client.DELETE('/task/{task_id}', {
      params: { path: { task_id: item.id } }
    })
    await handleData()
    void router.push('/generator')
  })
}

</script>
<template>
  <!--  <div class="row">-->
  <q-card class="container q-px-md q-py-xs">
    <q-tabs v-model="tab" :align="'left'" dense class="text-gray shadow-2"
            active-color="primary"
            indicator-color="primary">
      <q-icon class="cursor-pointer text-caption text-subtitle1 q-mr-md text-bold" name="add" @click="handleAddTask"/>
      <q-route-tab v-for="item in taskData" :key="`chart-${item.id}`" :name="`chart-${item.id}`" :label="item.name"
                   :to="`/generator/${item.id}`" exact>
        <q-menu touch-position context-menu>
          <q-list dense style="min-width: 100px">
            <q-item clickable v-close-popup @click="() => handleRename(item)">
              <q-item-section>重命名</q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="() => handleDelete(item)">
              <q-item-section class="text-red-5">删除</q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-route-tab>
    </q-tabs>
    <q-separator class="q-mb-md"/>
    <div v-if="taskData.length > 0" class="router">
      <router-view/>
    </div>
    <div v-else class="flex column flex-center" style="height: 400px">
      <div class="text-h5">
        目前还没有数据哦~😅
      </div>
      <div class="text-subtitle1 text-tip q-mt-sm">
        快点击左上角 + 号进行添加吧!
      </div>
    </div>
  </q-card>
  <!--    <q-card style="width: 10rem;min-width: 10rem; ">-->
  <!--      <q-list dense padding class="rounded-borders text-primary full-width full-height column">-->
  <!--        <q-item-label header class="row justify-between items-center q-py-sm">-->
  <!--          <div class="text-caption">任务</div>-->
  <!--          <q-icon class="cursor-pointer text-caption" name="add" @click="handleAddTask" />-->
  <!--        </q-item-label>-->
  <!--        <q-separator />-->
  <!--        <q-scroll-area class="full-width" style="flex: 1;">-->
  <!--          <template v-if="taskData.length > 0">-->
  <!--            <q-item v-for="item in taskData" class="text-base" :key="item.id" :to="`/task/${item.id}`"-->
  <!--              active-class="active-link text-primary" dense clickable v-ripple>-->
  <!--              <q-item-section class="ellipsis">-->
  <!--                {{ item.name }}-->
  <!--                <q-menu touch-position context-menu>-->
  <!--                  <q-list dense style="min-width: 100px">-->
  <!--                    <q-item clickable v-close-popup @click="() => handleRename(item)">-->
  <!--                      <q-item-section>重命名</q-item-section>-->
  <!--                    </q-item>-->
  <!--                    <q-item clickable v-close-popup @click="() => handleDelete(item)">-->
  <!--                      <q-item-section class="text-red-5">删除</q-item-section>-->
  <!--                    </q-item>-->
  <!--                  </q-list>-->
  <!--                </q-menu>-->
  <!--              </q-item-section>-->
  <!--              <q-tooltip anchor="top middle" :delay="500">-->
  <!--                {{ item.name }}-->
  <!--              </q-tooltip>-->
  <!--            </q-item>-->
  <!--          </template>-->
  <!--          <template v-else>-->
  <!--            <q-item-label header class="row items-center q-py-sm">-->
  <!--              <div class="text-caption text-grey-4">当前列表为空</div>-->
  <!--            </q-item-label>-->
  <!--          </template>-->
  <!--        </q-scroll-area>-->
  <!--      </q-list>-->
  <!--    </q-card>-->
  <!--    <template v-if="route.params.id && route.params.id !== ''">-->
  <!--      <router-view />-->
  <!--    </template>-->
  <!--    <div v-else style="flex: 1; margin-top: 5rem;"-->
  <!--      class="col flex column full-height full-width justify-center items-center text-grey-5">-->
  <!--      <q-icon class="text-h1" name="credit_score" />-->
  <!--      <div class="text-h6 q-mt-md">-->
  <!--        请在左侧选择一个任务后开始-->
  <!--      </div>-->
  <!--      <div class="text-subtitle">-->
  <!--        Please select one task from left side.-->
  <!--      </div>-->
  <!--    </div>-->
  <!--  </div>-->
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
