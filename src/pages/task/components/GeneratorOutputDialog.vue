<script setup lang="ts">
import { QScrollArea, useTimeout } from 'quasar'
import { ref } from 'vue'

const dialog = ref(false)
const output = ref('')
const scrollAreaRef = ref<null | InstanceType<typeof QScrollArea>>(null)

const {
  registerTimeout
} = useTimeout()
const openDialog = (str: string) => {
  output.value = str
  dialog.value = true
  registerTimeout(() => {
    const scroll = scrollAreaRef.value?.getScroll()
    if (scroll) {
      scrollAreaRef.value?.setScrollPosition('vertical', scroll.verticalSize, 500)
    }
  }, 100)
}

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

defineExpose({ openDialog })

</script>

<template>
  <div class="container">
    <q-dialog v-model="dialog" maximized position="right">
      <q-card class="bg-dark" style="width: 40rem;">
        <q-card-section class="full-height full-width overflow-hidden">
          <div class="text-h6 text-white">任务日志</div>
          <q-scroll-area ref="scrollAreaRef" class="q-mt-md" :thumb-style="thumbStyle" :bar-style="barStyle"
            style="height: 90%; width: 100%;">
            <div class="text-no-wrap text-grey-4" v-for="(item, index) in output.split('\n')" :key="`row-${index}`">
              {{ item }}
            </div>
          </q-scroll-area>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
