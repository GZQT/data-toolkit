<script setup lang="ts">
import { useQuasar } from 'quasar'
import { components } from 'src/types/api'
import { handleOpenFile } from 'src/utils/action'
import { isImage, whiteBarStyle, whiteThumbStyle } from 'src/utils/constant'
import { computed, ref } from 'vue'
import { TableExtend } from '../TaskGenerator.vue'
import PreviewChartDialog from './PreviewChartDialog.vue'

const $q = useQuasar()
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

defineExpose({
  openDialog
})

const handlePreview = (file: string) => {
  $q.dialog({
    component: PreviewChartDialog,
    componentProps: {
      file
    }
  })
}

const getFileNameFromPath = (filePath: string): string => {
  const separator = filePath.includes('/') ? '/' : '\\'
  const parts = filePath.split(separator)
  const fileName = parts.pop()!

  return fileName
}

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
          <q-scroll-area class="q-mt-md" :thumb-style="whiteThumbStyle" :bar-style="whiteBarStyle"
            style="flex: 1; width: 100%;">
            <div class="chart-area">
              <q-intersection v-for="(item) in imageFiles" :key="item" transition="scale"
                style="width: 380px; height: 200px;">
                <div>
                  <q-img class="full-width full-height " :src="item.replace(/#/g, '%23').replace(/\s/g, '%20')"
                    width="100%" height="100%" fit="fill" @click="handlePreview(item)">
                    <div class="absolute-bottom  text-center ellipsis cursor-pointer" @click="handleOpenFile(item)">
                      {{ getFileNameFromPath(item) }}
                      <q-tooltip>
                        {{ getFileNameFromPath(item) }}
                      </q-tooltip>
                    </div>
                  </q-img>
                </div>
              </q-intersection>
            </div>
          </q-scroll-area>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss">
.chart-area {
  display: grid;
  grid-gap: 10px;
  grid-auto-flow: dense;
  grid-template-columns: repeat(4, 1fr);
}

@media (max-width: $breakpoint-lg-max) {
  .chart-area {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
