<script setup lang="ts">
import { QScrollArea, useInterval, useTimeout } from 'quasar'
import { client } from 'src/boot/request'
import { components } from 'src/types/api'
import { computed, ref, watch } from 'vue'

const dialog = ref(false)
const id = ref<number>(0)
const taskId = ref<number>(0)
const generator = ref<components['schemas']['GeneratorAllResponse'] | undefined>()
const scrollAreaRef = ref<null | InstanceType<typeof QScrollArea>>(null)
const { registerInterval, removeInterval } = useInterval()

const {
  registerTimeout
} = useTimeout()

const getData = async () => {
  if (id.value <= 0) {
    return
  }
  const { data } = await client.GET('/task/{task_id}/generator/{generator_id}', {
    params: { path: { task_id: taskId.value, generator_id: id.value } }
  })
  generator.value = data
  handleToButton()
}

watch(id, getData)

const thumbStyle: Partial<CSSStyleDeclaration> = {
  right: '4px',
  borderRadius: '7px',
  backgroundColor: '#027be3',
  width: '4px',
  opacity: '0.75'
}

const barStyle: Partial<CSSStyleDeclaration> = {
  right: '2px',
  borderRadius: '9px',
  backgroundColor: '#027be3',
  width: '8px',
  opacity: '0.2'
}

const handleClose = () => {
  removeInterval()
}

const handleToTop = () => {
  scrollAreaRef.value?.setScrollPosition('vertical', 0, 500)
}

const handleToButton = () => {
  const scroll = scrollAreaRef.value?.getScroll()
  if (scroll) {
    scrollAreaRef.value?.setScrollPosition('vertical', scroll.verticalSize, 500)
  }
}

const handleClear = async () => {
  await client.PUT('/task/{task_id}/generator/{generator_id}/clearOutput', {
    params: { path: { task_id: taskId.value, generator_id: id.value } }
  })
  await getData()
}

const openDialog = (taskIdValue: number, idValue: number) => {
  id.value = idValue
  taskId.value = taskIdValue
  dialog.value = true
  registerTimeout(handleToButton, 100)
  registerInterval(getData, 3000)
}

defineExpose({ openDialog })

const status = computed(() => {
  if (!generator.value) {
    return 'red'
  }
  if (generator.value.status === 'FAILED') {
    return 'red'
  }
  if (generator.value.status === 'SUCCESS') {
    return 'green'
  }
  return 'yellow'
})

</script>

<template>
  <div class="container">
    <q-dialog v-model="dialog" maximized position="right" @hide="handleClose">
      <q-card class="bg-dark" style="width: 40rem;">
        <q-card-section class="full-height full-width overflow-hidden column">
          <div class="text-white row items-center">
            <div class="text-h6">任务日志</div>
            <q-badge rounded :color="status" class="q-ml-sm" style="width: 12px;height: 12px;transition: all 1s;" />
            <q-space />
            <q-btn flat round icon="close" @click="dialog = false" />
          </div>
          <q-scroll-area ref="scrollAreaRef" class="q-mt-md" :thumb-style="thumbStyle" :bar-style="barStyle"
            style="flex: 1; width: 100%;">
            <template v-if="generator && generator.output">
              <div class="text-no-wrap text-grey-4" v-for="(item, index) in generator.output.split('\n')"
                :key="`row-${index}`">
                {{ item }}
              </div>
            </template>
            <div v-else class="text-no-wrap text-grey-4">
              当前任务暂无日志信息
            </div>
          </q-scroll-area>
          <q-separator color="grey-6" />
          <div class="q-mt-md row">
            <q-btn flat round color="grey-8" icon="refresh" @click="getData">
              <q-tooltip>刷新</q-tooltip>
            </q-btn>
            <q-btn flat round color="grey-8" icon="keyboard_double_arrow_up" @click="handleToTop">
              <q-tooltip>回到顶部</q-tooltip>
            </q-btn>
            <q-btn flat round color="grey-8" icon="keyboard_double_arrow_down" @click="handleToButton">
              <q-tooltip>回到底部</q-tooltip>
            </q-btn>
            <q-space />
            <q-btn outline color="red-5" label="清除" @click="handleClear" />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
