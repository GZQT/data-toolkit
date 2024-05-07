<script setup lang="ts">
import _ from 'lodash'
import { client } from 'src/boot/request'
import { components } from 'src/types/api'
import { reactive, ref } from 'vue'

interface SelectOption {
  label: string
  value: number
}

interface FormSchema {
  averageBarGroupSelect: SelectOption[][],
  maxMinBarGroupSelect: SelectOption[][]
}

const dialog = ref(false)
const generatorId = ref<number>(0)
const fileList = ref<string[]>([])
const form = reactive<components['schemas']['TaskGeneratorStartRequest'] & FormSchema>({
  averageLineChart: true,
  maxMinLineChart: true,
  averageBarChart: false,
  maxMinBarChart: false,
  averageDataTable: true,
  maxMinDataTable: true,
  averageBarGroup: [],
  maxMinBarGroup: [],
  averageBarGroupSelect: [],
  maxMinBarGroupSelect: []
})
const columnNameGroup = ref<SelectOption[]>([])
const status = ref<components['schemas']['GeneratorResultEnum']>('PROCESSING')
const loading = ref(false)

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

const openDialog = (id: number, files: string[], currentStatus: components['schemas']['GeneratorResultEnum']) => {
  dialog.value = true
  generatorId.value = id
  fileList.value = files
  columnNameGroup.value = []
  form.averageLineChart = true
  form.maxMinLineChart = true
  form.averageBarChart = false
  form.maxMinBarChart = false
  form.averageDataTable = true
  form.maxMinDataTable = true
  form.averageBarGroup = []
  form.maxMinBarGroup = []
  form.averageBarGroupSelect = []
  form.maxMinBarGroupSelect = []
  status.value = currentStatus
}

defineExpose({
  openDialog
})

const handleAddBarGroup = async (key: 'averageBarGroupSelect' | 'maxMinBarGroupSelect') => {
  if (columnNameGroup.value.length === 0) {
    const filePath = fileList.value[0]
    const lines = await window.FileApi.getCsvHeader(filePath)

    columnNameGroup.value = lines.map((item, index) => ({
      label: item,
      value: index
    }))
  }
  form[key].push([])
}

const handleBarSelect = (index: number, key: 'averageBarGroup' | 'maxMinBarGroup', value: SelectOption[]) => {
  const data = _.cloneDeep(form[`${key}Select`])
  _.fill(data, value, index, index + 1)
  form[`${key}Select`] = data
  form[key] = _.map(data, innerArray =>
    _.map(innerArray, obj => obj.value)
  )
}

</script>

<template>
  <div class="container">
    <q-dialog v-model="dialog" persistent>
      <q-card style="min-width: 350px">
        <q-banner v-if="status === 'SUCCESS' || status !== 'PROCESSING'" inline-actions class="text-white bg-primary">
          TIP：当前任务已经 {{ status === 'SUCCESS' ? '执行过了' : '提交过了' }}，再次提交会覆盖掉上次内容
        </q-banner>
        <q-banner v-else-if="status === 'PROCESSING'" inline-actions class="text-white bg-primary">
          TIP：当前任务可能已经在运行了，再次提交会覆盖掉上次内容
        </q-banner>
        <q-card-section>
          <div class="text-subtitle1">
            启动任务
          </div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <div>
            <q-checkbox left-label v-model="form.averageLineChart" label="生成平均值折线图" />
            <q-checkbox left-label v-model="form.maxMinLineChart" label="生成最大最小值折线图" />
          </div>
          <div>
            <q-checkbox left-label v-model="form.averageDataTable" label="生成平均值数据表格" />
            <q-checkbox left-label v-model="form.maxMinDataTable" label="生成最大最小值数据表格" />
          </div>
          <div>
            <q-checkbox left-label v-model="form.maxMinBarChart" label="生成最大最小值柱状图" />
            <q-btn v-if="form.maxMinBarChart" flat rounded color="secondary"
              @click="() => handleAddBarGroup('maxMinBarGroupSelect')">添加对比组</q-btn>
          </div>
          <div v-if="form.maxMinBarChart">
            <template v-for="(item, index) in form.maxMinBarGroupSelect" :key="index">
              <q-select :model-value="item"
                @update:model-value="(select) => handleBarSelect(index, 'maxMinBarGroup', select)" multiple
                :options="columnNameGroup" :label="`选择对比列-${index + 1}`" />
            </template>
          </div>
        </q-card-section>
        <q-card-actions :align="'right'" class="text-primary">
          <q-btn flat label="取消" v-close-popup @click="dialog = false" />
          <q-btn flat label="确认" :loading="loading" @click="handleSubmit" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
