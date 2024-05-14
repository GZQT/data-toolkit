<script setup lang="ts">
import _ from 'lodash'
import { useQuasar } from 'quasar'
import { client } from 'src/boot/request'
import { components } from 'src/types/api'
import { GeneratorStartLineDialogForm } from 'src/types/generator'
import { computed, reactive, ref } from 'vue'
import GeneratorStartLineDialog from './GeneratorStartLineDialog.vue'

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
  averageBarChart: false,
  maxMinBarChart: false,
  averageDataTable: false,
  maxMinDataTable: false,
  rootMeanSquareDataTable: false,
  averageBarGroup: [],
  maxMinBarGroup: []
})
export type ConfigChartType = 'average' | 'maxMin' | 'rootMeanSquare'
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
  form.averageLineChart = _.cloneDeep(defaultLineChartParam)
  form.maxMinLineChart = _.cloneDeep(defaultLineChartParam)
  form.rootMeanSquareLineChart = _.cloneDeep(defaultLineChartParam)
  form.averageBarGroup = []
  form.maxMinBarGroup = []
  status.value = currentStatus
  const file = files[0]
  columns.value = await window.FileApi.getCsvHeader(file)
}

defineExpose({
  openDialog
})

const averageLineChartColumnLength = computed(() => {
  return form.averageLineChart.columnIndex?.length ?? 0
})
const maxMinLineChartColumnLength = computed(() => {
  return form.maxMinLineChart.columnIndex?.length ?? 0
})
const rootMeanSquareLineChartColumnLength = computed(() => {
  return form.rootMeanSquareLineChart.columnIndex?.length ?? 0
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
          <div class="flex items-center">
            <q-checkbox left-label v-model="form.averageDataTable" label="生成平均值数据表格" />
            <q-checkbox left-label v-model="form.averageLineChart.generate" label="生成平均值折线图" />
            <q-space />
            <div class="text-tip q-mr-xs">
              {{ (averageLineChartColumnLength ?? 0) > 0 ? `已配置 ${averageLineChartColumnLength} 列` : '默认生成全部列' }}
            </div>
            <q-btn :disable="!form.averageLineChart.generate" color="secondary" flat round size="sm" icon="settings"
              @click="handleConfig('average')" />
          </div>
          <div class="flex items-center">
            <q-checkbox left-label v-model="form.maxMinDataTable" label="生成最值数据表格" />
            <q-checkbox left-label v-model="form.maxMinLineChart.generate" label="生成最值折线图" />
            <q-space />
            <div class="text-tip q-mr-xs">
              {{ (maxMinLineChartColumnLength ?? 0) > 0 ? `已配置 ${maxMinLineChartColumnLength} 列` : '默认生成全部列' }}
            </div>
            <q-btn :disable="!form.maxMinLineChart.generate" color="secondary" flat round size="sm" icon="settings"
              @click="handleConfig('maxMin')" />
          </div>
          <div class="flex items-center">
            <q-checkbox left-label v-model="form.rootMeanSquareDataTable" label="生成均方根数据表格" />
            <q-checkbox left-label v-model="form.rootMeanSquareLineChart.generate" label="生成均方根折线图" />
            <q-space />
            <div class="text-tip q-mr-xs">
              {{ (rootMeanSquareLineChartColumnLength ?? 0) > 0
                ? `已配置 ${rootMeanSquareLineChartColumnLength} 列`
                : '默认生成全部列' }}
            </div>
            <q-btn :disable="!form.rootMeanSquareLineChart.generate" color="secondary" flat round size="sm"
              icon="settings" @click="handleConfig('rootMeanSquare')" />
          </div>
        </q-card-section>
        <q-card-actions :align="'right'" class="text-primary">
          <q-btn outline label="取消" v-close-popup @click="dialog = false" />
          <q-btn outline label="确认" :loading="loading" @click="handleSubmit" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
