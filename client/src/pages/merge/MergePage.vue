<script setup lang="ts">
import { useMergeStore } from 'pages/merge/merge-store'
import { isDataColumn } from 'src/utils'
import { ref } from 'vue'
import { QFile } from 'quasar'

const store = useMergeStore()
const selectFiles = ref<QFile[]>([])

</script>

<template>
  <q-scroll-area style="height: calc(100vh - 70px)">
    <div class="flex row q-gutter-x-lg no-wrap q-mr-lg" style="height: calc(100vh - 90px)">
      <q-card v-for="(item, index) in store.mergeData" :key="`file-${index}`"
              class="flex column full-height no-wrap q-pa-md"
              style="min-width: 280px">
        <div class="flex row justify-between items-center">
          <div>文件</div>
          <q-space/>
          <q-icon class="cursor-pointer" @click="() => store.handleRemove(index)" name="close">
            <q-tooltip>
              移除
            </q-tooltip>
          </q-icon>
        </div>
        <div class="cursor-pointer text-tip " @click="() => selectFiles[index].pickFiles()">
          <div class="ellipsis" style="max-width: 280px">
            {{ (item.file ?? '点击进行文件选择').split('\\').pop()?.split('/').pop() }}
          </div>
        </div>
        <q-file
          ref="selectFiles"
          class="hidden"
          v-model="item.fileObj" outlined label="选择一个文件" dense
          :loading="item.loading"
          accept=".csv"
          @update:model-value="(value: File) => store.handleUpdateFile(value, index)"
        />
        <q-separator/>
        <q-scroll-area class="q-mt-sm full-height">
          <q-list dense class="q-mr-md">
            <q-item dense v-for="column in item.columns" :key="column" tag="label" v-ripple="!isDataColumn(column)"
                    :disable="!isDataColumn(column) || (store.data.baseColumn === column && store.data.baseFilePath === item.file)">
              <q-item-section avatar>
                <q-checkbox
                  :disable="!isDataColumn(column) || (store.data.baseColumn === column && store.data.baseFilePath === item.file)"
                  v-model="item.selectColumns" :val="column"/>
              </q-item-section>
              <q-item-section>
                <q-item-label>
                  {{ column }}
                  <q-icon v-if="store.data.baseColumn === column && store.data.baseFilePath === item.file"
                          color="orange" name="star"/>
                </q-item-label>
              </q-item-section>
              <q-menu touch-position context-menu>
                <q-list>
                  <q-item clickable v-close-popup @click="() => store.handleToBasePoint(index, item.file, column)">
                    <q-item-section>设置为基准点</q-item-section>
                  </q-item>
                </q-list>
              </q-menu>
            </q-item>
          </q-list>
        </q-scroll-area>
      </q-card>
      <q-card flat
              class="cursor-pointer flex bg-transparent column full-height no-wrap q-pa-md flex-center border-dashed q-mr-md"
              style="min-width: 280px" @click="() => store.handleAdd()">
        <q-icon class="text-base" size="48px" name="add"/>
      </q-card>
    </div>
  </q-scroll-area>

  <q-page-sticky position="bottom-right" :offset="[18, 18]">
    <q-btn :loading="store.data.loading" fab icon="merge" color="primary" @click="store.handleSubmit">
      <q-tooltip>
        合并
      </q-tooltip>
    </q-btn>
  </q-page-sticky>
</template>

<style scoped lang="scss">

</style>
