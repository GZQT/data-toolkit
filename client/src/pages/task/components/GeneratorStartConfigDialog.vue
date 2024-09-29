<script setup lang="ts">

import { QTableProps, useDialogPluginComponent, useQuasar } from 'quasar'
import { components } from 'src/types/api'
import { onMounted, reactive } from 'vue'
import GeneratorConfigConditionDialog from 'pages/task/components/GeneratorConfigConditionDialog.vue'
import { conditionColorMapping, conditionMapping } from 'src/utils/constant.ts'
import _ from 'lodash'

interface RowData {
  id: number
  name: string
  column: string
  expression: string
  conditions: components['schemas']['GeneratorDataCondition'][]
}

const props = defineProps<{
  columns: string[],
  data: components['schemas']['GeneratorConfigRequest-Input']
}>()

const tableColumns: QTableProps['columns'] = [
  { name: 'name', label: '变量名', field: 'name', align: 'left', style: 'width: 1rem' },
  { name: 'column', label: '列名', field: 'column', align: 'left', style: 'width: 1rem' },
  { name: 'expression', label: '计算(不写则使用原始值)', field: 'expression', align: 'left' },
  { name: 'conditions', label: '阈值设置', field: 'conditions', align: 'left' }
]
const $q = useQuasar()
defineEmits([
  ...useDialogPluginComponent.emits
])

const form = reactive<{
  config: components['schemas']['GeneratorConfigRequest-Input'],
  columnIndex: number[],
  rows: RowData[]
}>({
  config: {
    converters: [],
    dauConfig: []
  },
  columnIndex: [],
  rows: []
})

onMounted(() => {
  form.config = props.data
  const rows = props.columns
    .map((column, index) => ({
      id: index,
      name: `c${index + 1}`,
      column,
      expression: '',
      conditions: []
    } as RowData))
  props.data.converters.forEach(item => {
    const existColumn = rows.find(row => row.column === item.columnKey)
    if (existColumn) {
      existColumn.expression = item.expression
      existColumn.conditions = item.conditions ?? []
    }
  })
  form.rows = rows
})

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

const handleOk = () => {
  form.config.converters = form.rows.map(item => ({
    columnKey: item.column,
    ...item
  }))
  onDialogOK(form.config)
}
const handleCancel = () => {
  onDialogCancel()
}

const handleAddCondition = (row: RowData, index: number) => {
  $q.dialog({
    component: GeneratorConfigConditionDialog
  }).onOk(data => {
    const exist = form.rows[index]
    if (exist) {
      const cloneExist = _.cloneDeep(exist)
      cloneExist.conditions.push(data)
      form.rows[index] = cloneExist
    }
  })
}

const handleRemoveCondition = (row: RowData, index: number) => {
  row.conditions.splice(index, 1)
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
          <template v-slot:body-cell-conditions="props">
            <q-td :props="props" style="max-width: 180px">
              <div class="flex row q-gutter-sm" >
                <q-chip
                  text-color="white"
                  :color="conditionColorMapping[item.type as components['schemas']['GeneratorDataConditionType']]"
                  v-for="(item, index) in props.row.conditions"
                  removable
                  :key="index" dense @remove="() => handleRemoveCondition(props.row, index)">
                  {{conditionMapping[item.type as components["schemas"]["GeneratorDataConditionType"]]}}-
                  {{item.startTime}}开始-{{item.endTime}}结束-(值{{item.value}})
                </q-chip>
                <q-chip clickable class="text-caption" dense label="添加" @click="() => handleAddCondition(props.row, props.rowIndex)"/>
              </div>
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
