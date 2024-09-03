<script setup lang="ts">

import { barStyle, thumbStyle } from 'src/utils/constant'
import { QScrollArea, useDialogPluginComponent, useInterval, useTimeout } from 'quasar'
import { onMounted, ref, watch } from 'vue'
import { useApplicationStore } from 'stores/application-store'

const {
  dialogRef,
  onDialogHide,
  onDialogCancel
} = useDialogPluginComponent()

const applicationStore = useApplicationStore()
const scrollAreaRef = ref<null | InstanceType<typeof QScrollArea>>(null)
const { registerInterval: registerMore } = useInterval()
const { registerTimeout } = useTimeout()
const more = ref<string>('.')

const handleToTop = () => {
  scrollAreaRef.value?.setScrollPosition('vertical', 0, 500)
}

const handleToBottom = () => {
  const scroll = scrollAreaRef.value?.getScroll()
  if (scroll) {
    scrollAreaRef.value?.setScrollPosition('vertical', scroll.verticalSize, 500)
  }
}

onMounted(() => {
  registerMore(() => {
    if (more.value.length > 6) {
      more.value = ''
    }
    more.value += '.'
  }, 500)
  registerTimeout(handleToBottom, 100)
})

const handleClear = () => {
  applicationStore.logs = []
}

defineEmits([
  ...useDialogPluginComponent.emits
])

watch(applicationStore.logs, () => {
  if (applicationStore.autoToBottom) {
    handleToBottom()
  }
})

</script>

<template>
  <div class="container">
    <q-dialog ref="dialogRef" @hide="onDialogHide" position="right" maximized>
      <q-card class="bg-dark" style="width: 30rem;">
        <q-card-section class="full-height full-width overflow-hidden column">
          <div class="text-white row items-center">
            <div class="text-h6">后台日志</div>
            <q-space/>
            <q-btn flat round icon="close" @click="onDialogCancel"/>
          </div>
          <q-scroll-area ref="scrollAreaRef" class="q-mt-md" :thumb-style="thumbStyle" :bar-style="barStyle"
                         style="flex: 1; width: 100%;" id="output-scroll-area">
            <template v-if="applicationStore.logs.length > 0">
              <q-virtual-scroll
                scroll-target="#output-scroll-area > .scroll" class="text-no-wrap text-grey-4"
                :items="applicationStore.logs" v-slot="{ item, index }" :virtual-scroll-item-size="32">
                <div
                  :key="`line-${index}`"
                >
                  {{ item }}
                </div>
              </q-virtual-scroll>
              <div v-if="applicationStore.isRunning" class="text-no-wrap text-grey-4 text-subtitle2 q-mb-lg">{{
                  more
                }}
              </div>
            </template>
            <div v-else class="text-no-wrap text-grey-4">
              当前任务暂无日志信息
            </div>
          </q-scroll-area>
          <q-separator color="grey-6"/>
          <div class="q-mt-md row">
            <q-btn flat round color="grey-8" icon="keyboard_double_arrow_up" @click="handleToTop">
              <q-tooltip>回到顶部</q-tooltip>
            </q-btn>
            <q-btn flat round color="grey-8" icon="keyboard_double_arrow_down" @click="handleToBottom">
              <q-tooltip>回到底部</q-tooltip>
            </q-btn>
            <q-toggle class="text-grey-8" v-model="applicationStore.autoToBottom" label="自动滚动"/>
            <q-space/>
            <q-btn outline color="red-5" label="清除" @click="handleClear"/>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss">

</style>
