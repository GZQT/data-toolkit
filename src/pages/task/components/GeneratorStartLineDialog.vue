<script setup lang="ts">
import _ from 'lodash'
import { copyToClipboard, useDialogPluginComponent, useQuasar } from 'quasar'
import { GeneratorStartLineDialogForm } from 'src/types/generator'
import { onMounted, reactive, ref } from 'vue'
const props = defineProps<{
  columns: string[],
  data: GeneratorStartLineDialogForm
}>()

defineEmits([
  ...useDialogPluginComponent.emits
])
const $q = useQuasar()
const timeUnit = ref<string>('T')
const allChartName = ref<string>('时程曲线图')

const form = reactive<GeneratorStartLineDialogForm>({
  chartColumnIndex: [],
  chartTimeRange: '10',
  chartXLabel: '时间',
  chartYLabel: '值',
  chartXRotation: 90,
  chartName: [],
  chartFill: 'NONE',
  chartShowGrid: true,
  chartLineWidth: 1
})

const { dialogRef, onDialogOK, onDialogCancel } = useDialogPluginComponent()

const timeUnitList = [
  { label: '秒(S)', value: 'S' },
  { label: '分钟(T)', value: 'T' },
  { label: '小时(H)', value: 'H' },
  { label: '天(D)', value: 'D' },
  { label: '周(W)', value: 'W' },
  { label: '月(M)', value: 'M' },
  { label: '季度(Q)', value: 'Q' },
  { label: '年(Y)', value: 'Y' }
]

onMounted(() => {
  form.chartColumnIndex = props.data.chartColumnIndex
  form.chartTimeRange = props.data.chartTimeRange
  form.chartXLabel = props.data.chartXLabel
  form.chartYLabel = props.data.chartYLabel
  form.chartXRotation = props.data.chartXRotation
  form.chartName = props.data.chartName
})

const handleCheckFileName = (file?: string) => {
  if (!file || file.trim() === '') {
    return '这个是必填字段'
  }
  if (/[“*<>?\\\\/|:]/.test(file)) {
    return '不能包含特殊字符'
  }
  return true
}

const handleSubmit = () => {
  for (const index in form.chartName) {
    if (handleCheckFileName(form.chartName[index]) !== true) {
      $q.notify({ type: 'warning', message: `操作失败，第${index + 1}个图表名称${form.chartName[index]}为空或者包含特殊字符，无法生成` })
      return
    }
  }
  onDialogOK({
    ...form,
    unit: timeUnit.value
  })
}

const lastValues = ref<number[]>([])
const handleSelect = (values: number[]) => {
  for (const index in form.chartColumnIndex) {
    if (!form.chartName[index]) {
      form.chartName[index] = `${props.columns[form.chartColumnIndex[index]]}时程曲线图`
    }
  }
  const diff = _.difference(lastValues.value, values)
  if (diff.length === 1) {
    const index = _.indexOf(lastValues.value, diff[0])
    _.pullAt(form.chartName, index)
  }
  lastValues.value = values
}

const handleCopy = async (content: string) => {
  await copyToClipboard(content)
}

</script>

<template>
  <div class="container">
    <q-dialog ref="dialogRef" persistent maximized transition-show="slide-up" transition-hide="slide-down">
      <q-card class="flex column overflow-hidden">
        <q-bar class="bg-primary text-white">
          <div>配置折线图</div>
          <q-space />
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip>关闭</q-tooltip>
          </q-btn>
        </q-bar>

        <q-card-section class="row no-wrap" style="flex: 1">
          <div class="col-6 full-height" style="max-width: 420px;">
            <div class="text-tip">请选择要生成的列（不选则为全部生成）</div>
            <q-scroll-area class="full-height">
              <q-list class="q-my-sm" bordered separator v-if="columns.length > 0">
                <q-item dense v-for="(column, index) in columns" :key="column">
                  <q-item-section>
                    <q-checkbox v-model="form.chartColumnIndex" dense
                      :disable="column === 'time' || column === 'col0' || column === 'id'" :val="index"
                      :label="`(${index}) ${column}`" @update:model-value="handleSelect" />
                  </q-item-section>
                </q-item>
              </q-list>
            </q-scroll-area>
          </div>
          <q-scroll-area class=" col q-px-lg">
            <div class="column full-height">
              <q-input v-model="form.chartTimeRange" label="时间区间" hint="进行计算的时间区间(单位: S秒，T分钟，H小时，D天，W周，M月，Q季度，Y年)"
                type="number">
                <template v-slot:append>
                  <q-btn text flat :label="`${timeUnitList.find(item => item.value === timeUnit)?.label}`">
                    <q-menu auto-close>
                      <q-list style="width:100px">
                        <q-item v-for="unit in timeUnitList" :key="unit.value" :active="timeUnit === unit.value"
                          clickable @click="timeUnit = unit.value">
                          {{ unit.label }}
                        </q-item>
                      </q-list>
                    </q-menu>
                  </q-btn>
                </template>
              </q-input>
              <q-input class="q-mt-md" v-model="form.chartXLabel" label="X 轴标题" />
              <q-input class="q-mt-md" v-model="form.chartYLabel" label="Y 轴标题" />
              <div class="q-mt-md">X 轴旋转角度 （{{ form.chartXRotation }}°）</div>
              <div class="q-mx-sm">
                <q-slider v-model="form.chartXRotation" :min="-90" :max="90" :step="1" label />
              </div>
              <q-list bordered class="rounded-borders q-mt-md">
                <q-expansion-item group="config" label="其他配置" :caption="`对折线图的其他配置`">
                  <q-separator />
                  <q-card>
                    <q-card-section>
                      <div>线条宽度 （{{ form.chartLineWidth }}）</div>
                      <q-slider class="q-mx-xs" v-model="form.chartLineWidth" :min="0.05" :max="5" :step="0.05" label />
                      <q-toggle v-model="form.chartShowGrid" color="primary" label="折线图是否显示网格背景" />
                      <div>在区间内数据缺失时数据填充方式</div>
                      <div class="row">
                        <q-radio v-model="form.chartFill" val="NONE" label="不进行填充">
                          <q-tooltip anchor="top middle" self="center middle">不进行任何处理，折线可能会出现断点的情况</q-tooltip>
                        </q-radio>
                        <q-radio v-model="form.chartFill" val="FORWARD_FILL" label="向前填充">
                          <q-tooltip anchor="top middle"
                            self="center middle">在数据缺失时，会直接使用前一个存在数据的值，折线可能会呈现阶梯状</q-tooltip>
                        </q-radio>
                        <q-radio v-model="form.chartFill" val="BACKWARD_FILL" label="向后填充">
                          <q-tooltip anchor="top middle"
                            self="center middle">在数据缺失时，会直接使用后一个存在数据的值，折线可能会呈现阶梯状</q-tooltip>
                        </q-radio>
                        <q-radio v-model="form.chartFill" val="LINE" label="线性填充">
                          <q-tooltip anchor="top middle" self="center middle">直接将缺失数据两段进行连接，折线可能会出现明显棱角的情况</q-tooltip>
                        </q-radio>
                      </div>
                    </q-card-section>
                  </q-card>
                </q-expansion-item>
                <q-separator inset />
                <q-expansion-item group="config" label="配置每一列的生成的折线图名称"
                  :caption="`您可以不配置此项，默认情况下折现图名称为 ${form.chartColumnIndex.length === 0 ? '时程曲线图' : '列名称+时程曲线图'}。`">
                  <q-separator />
                  <q-card>
                    <q-card-section class="q-mt-none">
                      <div class="text-red-5" style="opacity: 0.7;">不包含以下任何字符：“、*、&lt;、&gt;、?、\、/、|、：</div>
                      <template v-if="form.chartColumnIndex.length === 0">
                        <q-input class="q-mt-none q-pt-none" v-model="allChartName" label="所有图表名称"
                          hint="未选择特定列，将会生成所有列，这里将会配置所有图表名称" :rules="[val => handleCheckFileName(val)]" />
                      </template>
                      <template v-else>
                        <q-input v-for="(_, index) in form.chartName" class="q-mt-none q-pt-none"
                          :key="`chart-name-${index}`" v-model="form.chartName[index]"
                          :rules="[val => handleCheckFileName(val)]"
                          :label="`${columns[form.chartColumnIndex[index]]} 的图表名称`">
                          <template v-slot:append>
                            <q-btn flat dense icon="content_copy"
                              @click="handleCopy(columns[form.chartColumnIndex[index]])">
                              <q-tooltip>复制列名</q-tooltip>
                            </q-btn>
                          </template>
                        </q-input>
                      </template>
                    </q-card-section>
                  </q-card>
                </q-expansion-item>
              </q-list>
            </div>
            <div class="full-width row justify-end items-center q-mt-md">
              <q-btn color="primary" outline label="取消" @click="onDialogCancel" />
              <q-btn class="q-ml-md" color="primary" outline label="确认" @click="handleSubmit" />
            </div>
          </q-scroll-area>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
