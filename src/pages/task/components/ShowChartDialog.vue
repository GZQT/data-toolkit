<script setup lang="ts">
import { components } from 'src/types/api'
import { handleOpenFile } from 'src/utils/action'
import { isImage } from 'src/utils/constant'
import { computed, ref } from 'vue'
import { TableExtend } from '../TaskGenerator.vue'

const dialog = ref(false)
const data = ref<(components['schemas']['GeneratorResponse'] & TableExtend)>()

const openDialog = (item: (components['schemas']['GeneratorResponse'] & TableExtend)) => {
  dialog.value = true
  data.value = item
}

const imageFiles = computed(() => {
  if (!data.value || !data.value.dirFiles) {
    return []
  }
  return data.value.dirFiles
    .filter(item => isImage(item))
})

const othersFiles = computed(() => {
  if (!data.value || !data.value.dirFiles) {
    return []
  }
  return data.value.dirFiles.filter(item => !isImage(item))
})

const thumbStyle: Partial<CSSStyleDeclaration> = {
  right: '4px',
  borderRadius: '7px',
  backgroundColor: '#fff',
  width: '4px',
  opacity: '0.75'
}

const barStyle: Partial<CSSStyleDeclaration> = {
  right: '2px',
  borderRadius: '9px',
  backgroundColor: '#fff',
  width: '8px',
  opacity: '0.2'
}

defineExpose({
  openDialog
})

</script>

<template>
  <div class="container">
    <q-dialog v-model="dialog" maximized transition-show="slide-up" transition-hide="slide-down">
      <q-card class="bg-primary text-white column">
        <q-bar>
          <q-space />
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip class="bg-white text-primary">关闭</q-tooltip>
          </q-btn>
        </q-bar>

        <q-card-section class="full-width overflow-hidden column" style="flex: 1;">
          <div class="text-h6">{{ data?.name }} 已存在图表信息</div>
          <q-scroll-area ref="scrollAreaRef" class="q-mt-md " :thumb-style="thumbStyle" :bar-style="barStyle"
            style="flex: 1; width: 100%;">
            <div class="row justify-evenly q-gutter-sm">
              <q-intersection v-for="(item) in imageFiles" :key="item" transition="scale"
                style="width: 400px; height: 200px;">
                <div style="width: 400px; height: 200px;">
                  <q-img class="full-width full-height cursor-pointer"
                    :src="item.replace(/#/g, '%23').replace(/\s/g, '%20')" width="100%" height="100%" fit="fill"
                    @click="handleOpenFile(item)" />
                </div>
              </q-intersection>
            </div>
          </q-scroll-area>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
