<script setup lang="ts">
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
const form = reactive<components['schemas']['TaskGeneratorStartRequest']>({
  averageLineChart: true,
  averageLineChartColumnIndex: [],
  averageLineChartTimeRange: '10',
  averageLineChartXLabel: '时间',
  averageLineChartYLabel: '值',
  averageLineChartXRotation: 90,
  averageLineChartName: [],
  averageLineChartLineWidth: 1,
  averageLineChartFill: 'NONE',
  averageLineChartShowGrid: true,

  maxMinLineChart: true,
  maxMinLineChartColumnIndex: [],
  maxMinLineChartTimeRange: '10',
  maxMinLineChartXLabel: '时间',
  maxMinLineChartYLabel: '值',
  maxMinLineChartXRotation: 90,
  maxMinLineChartName: [],
  maxMinLineChartLineWidth: 1,
  maxMinLineChartFill: 'NONE',
  maxMinLineChartShowGrid: true,

  averageBarChart: false,
  maxMinBarChart: false,
  averageDataTable: true,
  maxMinDataTable: true,
  averageBarGroup: [],
  maxMinBarGroup: []
})
export type ConfigChartType = 'averageLine' | 'maxMinLine'
const columnNameGroup = ref<SelectOption[]>([])
const status = ref<components['schemas']['GeneratorResultEnum']>('PROCESSING')
const loading = ref(false)
const columns = ref<string[]>([])
const currentConfig = ref<ConfigChartType>('averageLine')
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
  form.averageLineChart = false

  form.averageLineChartColumnIndex = []
  form.averageLineChartTimeRange = '10T'
  form.averageLineChartXLabel = '时间'
  form.averageLineChartYLabel = '值'
  form.averageLineChartXRotation = 90
  form.averageLineChartName = []
  form.averageLineChartLineWidth = 1
  form.averageLineChartFill = 'NONE'
  form.averageLineChartShowGrid = true

  form.maxMinLineChart = false
  form.maxMinLineChartColumnIndex = []
  form.maxMinLineChartTimeRange = '10T'
  form.maxMinLineChartXLabel = '时间'
  form.maxMinLineChartYLabel = '值'
  form.maxMinLineChartXRotation = 90
  form.maxMinLineChartName = []
  form.maxMinLineChartLineWidth = 1
  form.maxMinLineChartFill = 'NONE'
  form.maxMinLineChartShowGrid = true

  form.averageBarChart = false
  form.maxMinBarChart = false
  form.averageDataTable = true
  form.maxMinDataTable = true
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
  return form.averageLineChartColumnIndex?.length ?? 0
})
const maxMinLineChartColumnLength = computed(() => {
  return form.maxMinLineChartColumnIndex?.length ?? 0
})
const handleConfig = (config: ConfigChartType) => {
  currentConfig.value = config
  $q.dialog({
    component: GeneratorStartLineDialog,
    componentProps: {
      columns: columns.value,
      data: {
        chartColumnIndex: form[`${config}ChartColumnIndex`],
        chartTimeRange: form[`${config}ChartTimeRange`],
        chartXLabel: form[`${config}ChartXLabel`],
        chartYLabel: form[`${config}ChartYLabel`],
        chartXRotation: form[`${config}ChartXRotation`],
        chartName: form[`${config}ChartName`],
        chartLineWidth: form[`${config}ChartLineWidth`],
        chartFill: form[`${config}ChartFill`],
        chartShowGrid: form[`${config}ChartShowGrid`]
      }
    }
  }).onOk((data: GeneratorStartLineDialogForm & { unit: string }) => {
    form[`${config}ChartColumnIndex`] = data.chartColumnIndex
    form[`${config}ChartTimeRange`] = `${data.chartTimeRange}${data.unit}`
    form[`${config}ChartXLabel`] = data.chartXLabel
    form[`${config}ChartYLabel`] = data.chartYLabel
    form[`${config}ChartXRotation`] = data.chartXRotation
    form[`${config}ChartName`] = data.chartName
    form[`${config}ChartLineWidth`] = data.chartLineWidth
    form[`${config}ChartFill`] = data.chartFill
    form[`${config}ChartShowGrid`] = data.chartShowGrid
  }).onCancel(() => { })
}

</script>

<template>
  <div class="container">
    <q-dialog v-model="dialog" persistent>
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
          <div>
            <q-checkbox left-label v-model="form.averageDataTable" label="生成平均值数据表格" />
            <q-checkbox left-label v-model="form.maxMinDataTable" label="生成最大最小值数据表格" />
          </div>
          <div class="flex items-center">
            <q-checkbox left-label v-model="form.averageLineChart" label="生成平均值折线图" />
            <template v-if="form.averageLineChart">
              <q-space />
              <div class="text-tip q-mr-xs">
                {{ (averageLineChartColumnLength ?? 0) > 0 ? `已配置 ${averageLineChartColumnLength} 列` : '默认生成全部列' }}
              </div>
              <q-btn color="secondary" flat round size="sm" icon="settings" @click="handleConfig('averageLine')" />
            </template>
          </div>
          <div class="flex items-center">
            <q-checkbox left-label v-model="form.maxMinLineChart" label="生成最大最小值折线图" />
            <template v-if="form.maxMinLineChart">
              <q-space />
              <div class="text-tip q-mr-xs">
                {{ (maxMinLineChartColumnLength ?? 0) > 0 ? `已配置 ${maxMinLineChartColumnLength} 列` : '默认生成全部列' }}
              </div>
              <q-btn color="secondary" flat round size="sm" icon="settings" @click="handleConfig('maxMinLine')" />
            </template>
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
