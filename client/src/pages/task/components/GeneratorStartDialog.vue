<script setup lang="ts">
import _ from 'lodash'
import { useQuasar } from 'quasar'
import { client } from 'src/boot/request'
import { components } from 'src/types/api'
import { GeneratorStartLineDialogForm } from 'src/types/generator'
import { reactive, ref } from 'vue'
import GeneratorStartConfigDialog from './GeneratorStartConfigDialog.vue'
import GeneratorStartLineDialog from './GeneratorStartLineDialog.vue'
import { isElectron } from 'src/utils/action'

interface SelectOption {
  label: string
  value: number
}

const $q = useQuasar()
const dialog = ref(false)
const generatorId = ref<number>(0)
const fileList = ref<string[]>([])
const defaultLineChartParam: components['schemas']['LineChartRequest'] = {
  generate: false,
  columnIndex: [],
  timeRange: '10min',
  xLabel: '时间',
  yLabel: '值',
  xRotation: 90,
  name: [],
  lineWidth: 1,
  fill: 'NONE',
  showGrid: true
}
const form = reactive<components['schemas']['TaskGeneratorStartRequest']>({
  averageLineChart: _.cloneDeep(defaultLineChartParam),
  maxMinLineChart: _.cloneDeep(defaultLineChartParam),
  rootMeanSquareLineChart: _.cloneDeep(defaultLineChartParam),
  rawLineChart: _.cloneDeep(defaultLineChartParam),
  averageBarChart: false,
  maxMinBarChart: false,
  averageDataTable: false,
  maxMinDataTable: false,
  rootMeanSquareDataTable: false,
  rawDataTable: false,
  averageBarGroup: [],
  maxMinBarGroup: [],
  config: {
    converters: []
  }
})
export type ConfigChartType = 'average' | 'maxMin' | 'rootMeanSquare' | 'raw'
const columnNameGroup = ref<SelectOption[]>([])
const status = ref<components['schemas']['GeneratorResultEnum']>('PROCESSING')
const loading = ref(false)
const columns = ref<string[]>([])
const currentConfig = ref<ConfigChartType>('average')
const props = defineProps<{
  taskId: number
}>()

const handleSubmit = async () => {
  loading.value = true
  try {
    await client.POST('/task/{task_id}/generator/{generator_id}', {
      params: {
        path: {
          task_id: props.taskId,
          generator_id: generatorId.value
        }
      },
      body: form
    })
    dialog.value = false
  } finally {
    loading.value = false
  }
}

const openDialog = async (id: number, files: string[], currentStatus: components['schemas']['GeneratorResultEnum']) => {
  dialog.value = true
  generatorId.value = id
  fileList.value = files
  columnNameGroup.value = []
  form.rawLineChart = _.cloneDeep(defaultLineChartParam)
  form.averageLineChart = _.cloneDeep(defaultLineChartParam)
  form.maxMinLineChart = _.cloneDeep(defaultLineChartParam)
  form.rootMeanSquareLineChart = _.cloneDeep(defaultLineChartParam)
  form.averageBarGroup = []
  form.maxMinBarGroup = []
  form.config = {
    converters: []
  }
  status.value = currentStatus
  const file = files[0]
  if (!isElectron()) {
    return
  }
  columns.value = await window.FileApi.getCsvHeader(file)
}

defineExpose({
  openDialog
})

const handleConfig = (config: ConfigChartType) => {
  currentConfig.value = config
  $q.dialog({
    component: GeneratorStartLineDialog,
    componentProps: {
      columns: columns.value,
      data: form[`${config}LineChart`]
    }
  }).onOk((data: GeneratorStartLineDialogForm & { unit: string }) => {
    form[`${config}LineChart`].columnIndex = data.columnIndex
    form[`${config}LineChart`].timeRange = `${data.timeRange}${data.unit}`
    form[`${config}LineChart`].xLabel = data.xLabel
    form[`${config}LineChart`].yLabel = data.yLabel
    form[`${config}LineChart`].xRotation = data.xRotation
    form[`${config}LineChart`].name = data.name
    form[`${config}LineChart`].lineWidth = data.lineWidth
    form[`${config}LineChart`].fill = data.fill
    form[`${config}LineChart`].showGrid = data.showGrid
  }).onCancel(() => { })
}

const handleConfigDialog = () => {
  $q.dialog({
    component: GeneratorStartConfigDialog,
    componentProps: {
      columns: columns.value,
      data: form.config
    }
  }).onOk((config: components['schemas']['GeneratorConfigRequest']) => {
    form.config = config
  })
}

const chartList: { name: ConfigChartType, label: string }[] =
  [
    { name: 'raw', label: '原始值' },
    { name: 'average', label: '平均值' },
    { name: 'maxMin', label: '最值' },
    { name: 'rootMeanSquare', label: '均方根' }
  ]

</script>

<template>
  <div class="container">
    <q-dialog v-model="dialog">
      <q-card style="min-width: 350px">
        <q-banner v-if="status === 'SUCCESS' || status !== 'PROCESSING'" inline-actions class="text-white bg-primary">
          TIP：当前任务已经{{ status === 'SUCCESS' ? '执行过了' : '提交过了' }}，再次提交会覆盖掉上次内容
        </q-banner>
        <q-banner v-else-if="status === 'PROCESSING'" inline-actions class="text-white bg-primary">
          TIP：当前任务可能已经在运行了，再次提交会覆盖掉上次内容
        </q-banner>
        <q-card-section class="row">
          <div class="text-subtitle1">
            启动任务
          </div>
          <q-space />
          <q-btn flat round size="sm" icon="close" @click="dialog = false" />
        </q-card-section>
        <q-card-section class="q-pt-none">
          <div class="flex items-center" v-for="chart in chartList" :key="`chart-${chart.label}`">
            <q-checkbox left-label v-model="form[`${chart.name}DataTable`]" :label="`生成值${chart.label}数据表格`" />
            <q-checkbox left-label v-model="form[`${chart.name}LineChart`].generate" :label="`生成值${chart.label}折线图`" />
            <q-space />
            <div class="text-tip q-mr-xs">
              {{ (form[`${chart.name}LineChart`].columnIndex?.length ?? 0) > 0
              ? `已配置 ${(form[`${chart.name}LineChart`].columnIndex?.length ?? 0)} 列`
              : '默认生成全部列' }}
            </div>
            <q-btn :disable="!form[`${chart.name}LineChart`].generate" color="secondary" flat round size="sm"
              icon="settings" @click="handleConfig(chart.name)" />
          </div>
        </q-card-section>
        <q-card-actions class="flex text-primary">
          <q-btn outline label="数据预处理" color="secondary" @click="handleConfigDialog" />
          <q-space />
          <q-btn outline label="取消" v-close-popup />
          <q-btn outline label="确认" :loading="loading" @click="handleSubmit" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
