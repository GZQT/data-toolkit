<script setup lang="ts">
import _ from 'lodash'
import { useDialogPluginComponent, useQuasar } from 'quasar'
import { components } from 'src/types/api'
import { GeneratorStartLineDialogForm } from 'src/types/generator'
import { computed, onMounted, reactive, ref } from 'vue'
import GeneratorStartConfigDialog from './GeneratorStartConfigDialog.vue'
import GeneratorStartLineDialog from './GeneratorStartLineDialog.vue'
import { isElectron } from 'src/utils/action'
import { client } from 'boot/request'
import GeneratorStartDauConfigDialog from 'pages/task/components/GeneratorStartDauConfigDialog.vue'

const $q = useQuasar()
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
  saveData: false,
  averageBarGroup: [],
  maxMinBarGroup: [],
  config: {
    converters: [],
    dauConfig: []
  }
})
export type ConfigChartType = 'average' | 'maxMin' | 'rootMeanSquare' | 'raw'
const loading = ref(false)
const allColumns = ref<string[]>([])
const invalidColumnCount = ref(0)
const currentConfig = ref<ConfigChartType>('average')
const props = defineProps<{
  taskId: number,
  files: string[],
  id: number,
  currentStatus: components['schemas']['GeneratorResultEnum'],
  config: components['schemas']['GeneratorConfigRequest'] | null
}>()

const handleSubmit = async () => {
  loading.value = true
  try {
    await client.POST('/task/{task_id}/generator/{generator_id}', {
      params: {
        path: {
          task_id: props.taskId,
          generator_id: props.id
        }
      },
      body: form
    })
    onDialogOK()
  } finally {
    loading.value = false
  }
}

const {
  dialogRef,
  onDialogHide,
  onDialogOK,
  onDialogCancel
} = useDialogPluginComponent()

defineEmits({
  ...useDialogPluginComponent.emits
})

onMounted(async () => {
  const file = props.files[0]
  if (!isElectron()) {
    return
  }
  allColumns.value = await window.FileApi.getCsvHeader(file)
  if (props.config) {
    form.config = props.config
    console.log(form.config)
  }
})

const columns = computed(() => {
  return allColumns.value.filter(item => {
    return !item.includes('time') && !item.includes('id') && !item.includes('times') && !item.includes('col0')
  })
})

const handleConfig = (config: ConfigChartType) => {
  currentConfig.value = config
  $q.dialog({
    component: GeneratorStartLineDialog,
    componentProps: {
      columns: allColumns.value,
      data: form[`${config}LineChart`],
      invalidColumnCount: invalidColumnCount.value
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
  })
}

const handleConfigDialog = () => {
  $q.dialog({
    component: GeneratorStartConfigDialog,
    componentProps: {
      columns: columns.value,
      data: form.config
    }
  }).onOk((config: components['schemas']['GeneratorConfigRequest']) => {
    form.config = {
      converters: config.converters,
      dauConfig: form.config?.dauConfig ?? []
    }
  })
}

const handleDauConfigDialog = () => {
  $q.dialog({
    component: GeneratorStartDauConfigDialog,
    componentProps: {
      columns: columns.value,
      dauConfig: form.config?.dauConfig ?? []
    }
  }).onOk((config: components['schemas']['DauConfig'][]) => {
    form.config = {
      converters: form.config?.converters ?? [],
      dauConfig: config
    }
  })
}

const chartList: { name: ConfigChartType, label: string }[] =
  [
    {
      name: 'raw',
      label: '原始值'
    },
    {
      name: 'average',
      label: '平均值'
    },
    {
      name: 'maxMin',
      label: '最值'
    },
    {
      name: 'rootMeanSquare',
      label: '均方根'
    }
  ]

</script>

<template>
  <div class="container">
    <q-dialog ref="dialogRef" @hide="onDialogHide">
      <q-card style="min-width: 350px">
        <q-banner v-if="currentStatus === 'SUCCESS' || currentStatus !== 'PROCESSING'" inline-actions
                  class="text-white bg-primary">
          TIP：当前任务已经{{ currentStatus === 'SUCCESS' ? '执行过了' : '提交过了' }}，再次提交会覆盖掉上次内容
        </q-banner>
        <q-banner v-else-if="currentStatus === 'PROCESSING'" inline-actions class="text-white bg-primary">
          TIP：当前任务可能已经在运行了，再次提交会覆盖掉上次内容
        </q-banner>
        <q-card-section class="row">
          <div class="text-subtitle1">
            启动任务
          </div>
          <q-space/>
          <q-btn flat round size="sm" icon="close" @click="onDialogCancel"/>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <div class="flex items-center" v-for="chart in chartList" :key="`chart-${chart.label}`">
            <q-checkbox left-label v-model="form[`${chart.name}DataTable`]" :label="`生成值${chart.label}数据表格`"/>
            <q-checkbox left-label v-model="form[`${chart.name}LineChart`].generate"
                        :label="`生成值${chart.label}折线图`"/>
            <q-space/>
            <div class="text-tip q-mr-xs">
              {{
                (form[`${chart.name}LineChart`].columnIndex?.length ?? 0) > 0
                  ? `已配置 ${(form[`${chart.name}LineChart`].columnIndex?.length ?? 0)} 列`
                  : '默认生成全部列'
              }}
            </div>
            <q-btn :disable="!form[`${chart.name}LineChart`].generate" color="secondary" flat round size="sm"
                   icon="settings" @click="handleConfig(chart.name)"/>
          </div>
          <q-checkbox left-label v-model="form.saveData" label="另存为处理过的数据" />
          <span class="text-tip text-caption">（选择一个折线图后有效，最大最小值暂不支持此功能）</span>
        </q-card-section>
        <q-card-actions class="flex text-primary">
          <q-btn outline color="secondary" @click="handleConfigDialog">
            数据预处理
            <q-icon v-if="form.config && form.config.converters && form.config.converters.length > 0" class="q-pl-xs"
                    size="16px" name="check_circle"/>
          </q-btn>
          <q-btn outline color="secondary" @click="handleDauConfigDialog">
            DAU 配置
            <q-icon v-if="form.config && form.config.dauConfig && form.config.dauConfig.length > 0" class="q-pl-xs"
                    size="16px" name="check_circle"/>
          </q-btn>
          <q-space/>
          <q-btn outline label="取消" v-close-popup/>
          <q-btn outline label="确认" :loading="loading" @click="handleSubmit"/>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
