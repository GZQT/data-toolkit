<script setup lang="ts">

import { useDialogPluginComponent } from 'quasar'
import { useMergeStore } from 'pages/merge/merge-store'
import { onMounted, reactive, watch } from 'vue'
import { isDataColumn } from 'src/utils'

interface Data {
  base: {
    fileName?: string
    filePath?: string
    column?: string
  }
}

const store = useMergeStore()
defineEmits([
  ...useDialogPluginComponent.emits
])

const {
  dialogRef,
  onDialogHide,
  onDialogOK,
  onDialogCancel
} = useDialogPluginComponent()
const data = reactive<Data>({
  base: {}
})

onMounted(() => {

})

watch(() => data.base.filePath, (value, oldValue) => {
  console.log(value, oldValue)
})

const handleSave = () => {
  onDialogOK()
}

</script>

<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <q-card class="q-dialog-plugin">
      <q-card-section class="flex justify-between items-center">
        <div class="text-h6">合并信息配置</div>
        <q-btn flat round @click="onDialogCancel" icon="close"/>
      </q-card-section>
      <q-card-section class="flex column q-gutter-y-md">
        <q-select
          label="指定一个基准点文件"
          dense
          class="full-width ellipsis"
          v-model="data.base.filePath"
          :options="store.mergeData.filter(item => item.file)"
          option-value="file"
          option-label="fileName"
          emit-value
          outlined
        >
          <template v-slot:selected-item="scope">
            <div class="overflow-hidden ellipsis full-width">
              {{scope.opt}}
            </div>
          </template>
        </q-select>
        <q-select
          label="指定一个基准点"
          dense
          class="full-width ellipsis"
          v-model="data.base.column"
          :options="(store.mergeData.find(item => item.file === data.base.filePath)?.columns ?? []).filter(item => isDataColumn(item))"
          popup-content-style="height: 200px"
          outlined
        >
          <template v-slot:selected-item="scope">
            <div class="overflow-hidden ellipsis full-width">
              {{scope.opt}}
            </div>
          </template>
        </q-select>
      </q-card-section>
      <q-card-actions align="right">
        <!--        <q-btn color="primary" label="OK" @click="onOKClick" />-->
        <q-btn color="red" outline label="取消" @click="onDialogCancel"/>
        <q-btn color="primary" outline label="保存" @click="handleSave"/>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<style scoped lang="scss">

</style>
