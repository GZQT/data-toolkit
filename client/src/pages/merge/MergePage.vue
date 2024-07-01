<script setup lang="ts">
import { useMergeStore } from 'stores/merge-store'
import { isDataColumn } from 'src/utils'
import { useQuasar } from 'quasar'
import MergeConfirmDialog from 'pages/merge/MergeConfirmDialog.vue'

const store = useMergeStore()
const $q = useQuasar()

const handleConfirm = () => {
  $q.dialog({
    component: MergeConfirmDialog
  })
}

</script>

<template>
  <q-scroll-area style="height: calc(100vh - 70px)">
    <div class="flex row q-gutter-x-lg no-wrap q-mr-lg" style="height: calc(100vh - 90px)">
      <q-card v-for="(item, index) in store.mergeData" :key="`file-${index}`" class="flex column full-height no-wrap q-pa-md"
              style="min-width: 280px">
        <div class="flex row justify-between items-center">
          <div>文件-{{index + 1}}</div>
          <q-space />
          <q-icon class="cursor-pointer" @click="() => store.handleRemove(index)" name="close" />
        </div>
        <q-file
          class="q-mt-sm"
          v-model="item.fileObj" outlined label="选择一个文件" dense
          :loading="item.loading"
          accept=".csv"
          @update:model-value="(value: File) => store.handleUpdateFile(value, index)"
        />
        <q-scroll-area class="q-mt-sm full-height">
          <q-list dense class="q-mr-md">
            <q-item dense v-for="column in item.columns" :key="column" tag="label" v-ripple="!isDataColumn(column)" :disable="!isDataColumn(column)">
              <q-item-section avatar>
                <q-checkbox :disable="!isDataColumn(column)" v-model="item.selectColumns" :val="column" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ column }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-scroll-area>
      </q-card>
      <q-card flat class="cursor-pointer flex bg-transparent column full-height no-wrap q-pa-md flex-center border-dashed q-mr-md"
              style="min-width: 280px" @click="() => store.handleAdd()">
        <q-icon class="text-base" size="48px" name="add" />
      </q-card>
    </div>
  </q-scroll-area>

  <q-page-sticky position="bottom-right" :offset="[18, 18]">
    <q-btn fab icon="merge" color="primary" @click="handleConfirm">
      <q-tooltip>
        合并
      </q-tooltip>
    </q-btn>
  </q-page-sticky>
</template>

<style scoped lang="scss">

</style>
