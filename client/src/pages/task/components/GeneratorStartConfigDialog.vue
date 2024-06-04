<script setup lang="ts">

import { QTableProps, useDialogPluginComponent } from 'quasar'
import { components } from 'src/types/api'
import { onMounted, reactive } from 'vue'

interface RowData {
  id: number
  name: string
  column: string
  expression: string
}

const props = defineProps<{
  columns: string[],
  data: components['schemas']['GeneratorConfigRequest']
}>()

const tableColumns: QTableProps['columns'] = [
  { name: 'id', label: '列数', field: 'id', align: 'left', style: 'width: 1rem' },
  { name: 'name', label: '变量名', field: 'name', align: 'left', style: 'width: 1rem' },
  { name: 'column', label: '列名', field: 'column', align: 'left', style: 'width: 1rem' },
  { name: 'expression', label: '计算(不写则使用原始值)', field: 'expression', align: 'left' }
]

defineEmits([
  ...useDialogPluginComponent.emits
])

const form = reactive<{
  config: components['schemas']['GeneratorConfigRequest'],
  columnIndex: number[],
  rows: RowData[]
}>({
  config: {
    converters: []
  },
  columnIndex: [],
  rows: []
})

onMounted(() => {
  form.config = props.data
  const rows = props.columns
    .map((column, index) => ({
      id: index,
      name: `c${index}`,
      column,
      expression: ''
    }))
    .filter(item => {
      return !item.column.includes('time') && !item.column.includes('id') && !item.column.includes('times')
    })
  form.config.converters.forEach(item => {
    const existColumn = rows.find(row => row.column === item.columnKey)
    if (existColumn) {
      existColumn.expression = item.expression
    }
  })
  form.rows = rows
})

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

const handleOk = () => {
  form.config.converters = form.rows.map(item => ({
    columnKey: item.column,
    expression: item.expression
  }))
  onDialogOK(form.config)
}
const handleCancel = () => {
  onDialogCancel()
}

</script>

<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" :maximized="true" transition-show="slide-up"
    transition-hide="slide-down">
    <q-card class="flex column ">
      <q-bar class="bg-primary text-white full-width fixed" style="z-index: 10;">
        <div>全局数据配置</div>
        <q-space />
        <q-btn dense flat icon="close" v-close-popup>
          <q-tooltip>关闭</q-tooltip>
        </q-btn>
      </q-bar>
      <q-scroll-area class="full-height q-mt-lg q-px-md">
        <q-table :pagination="{ rowsPerPage: 0 }" title="数据预处理配置" class="q-pa-xs" :rows="form.rows"
          :columns="tableColumns" :hide-pagination="true" row-key="id">
          <template v-slot:body-cell-expression="props">
            <q-td :props="props">
              <div v-if="props.row.column === 'time' || props.row.column === 'col0' || props.row.column === 'id'">
                当前列不支持进行此操作</div>
              <q-input v-else class="full-width" :dense="true" v-model="props.row.expression" />
            </q-td>
          </template>
          <template v-slot:top-right>
            <div class="flex row q-gutter-md">
              <q-btn color="primary" label="取消" outline no-caps v-close-popup @click="handleCancel" />
              <q-btn class="q-ml-2" color="primary" label="保存" outline @click="handleOk" />
            </div>
          </template>
        </q-table>
      </q-scroll-area>
    </q-card>
  </q-dialog>
</template>

<style scoped lang="scss"></style>
