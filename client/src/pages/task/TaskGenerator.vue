<script setup lang="tsx">
import _ from 'lodash'
import { QChip, QTableProps, useInterval, useQuasar } from 'quasar'
import { client } from 'src/boot/request'
import { components } from 'src/types/api'
import { handleHomeDirectoryOpenFile, handleOpenFile, isElectron } from 'src/utils/action'
import { GENERATOR_FILE_SPLIT } from 'src/utils/constant'
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import GeneratorOutputDialog from './components/GeneratorOutputDialog.vue'
import GeneratorStartBarDialog from './components/GeneratorStartBarDialog.vue'
import GeneratorStartDialog from './components/GeneratorStartDialog.vue'
import ShowChartDialog from './components/ShowChartDialog.vue'
import GeneratorEditDialog from 'pages/task/components/GeneratorEditDialog.vue'

export interface TableExtend {
  total?: number
  chartTotal?: number
  dataTotal?: number
  dirFiles?: string[]
}
export type GeneratorType = components['schemas']['GeneratorResponse'] & TableExtend

const { registerInterval, removeInterval } = useInterval()
const refreshTime = ref<number>(5)
const taskGeneratorData = ref<(GeneratorType)[]>([])
const columns: QTableProps['columns'] = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'name', label: '批次', field: 'name', align: 'left', sortable: true },
  { name: 'status', label: '状态', field: 'status', align: 'left' },
  { name: 'total', label: '文件数', field: 'total', align: 'left' },
  { name: 'chartTotal', label: '图表数', field: 'total', align: 'left' },
  { name: 'dataTotal', label: '数据行数', field: 'total', align: 'left' },
  { name: 'result', label: '执行结果', field: 'result', align: 'left' },
  { name: 'action', label: '操作', field: 'name', align: 'center' }
]

const $q = useQuasar()
const route = useRoute()
const taskId = ref<number>(0)
const generatorOutputDialog = ref<null | InstanceType<typeof GeneratorOutputDialog>>(null)
const showChartDialog = ref<null | InstanceType<typeof ShowChartDialog>>(null)
const generatorStartBarDialog = ref<null | InstanceType<typeof GeneratorStartBarDialog>>(null)
const selected = ref<(GeneratorType)[]>([])
const filter = ref('')
const generatorFile = ref<Record<number, TableExtend>>({})
const loading = reactive({
  table: false,
  refresh: false,
  count: false
})

const checkNewState = (data: (GeneratorType)[], status: components['schemas']['GeneratorResultEnum']) => {
  return taskGeneratorData.value.filter(item => item.status === status).length < (data.filter(item => item.status === status).length ?? 0) &&
    taskGeneratorData.value.length > 0
}

const handleData = async () => {
  const lastTask = taskId.value
  taskId.value = Number(route.params.id as string)
  try {
    loading.table = true
    loading.refresh = true
    const { data } = await client.GET('/task/{task_id}/generator', { params: { path: { task_id: taskId.value } } })
    if (!data) {
      taskGeneratorData.value = []
      return
    }
    if (lastTask === taskId.value) {
      if (checkNewState(data, 'SUCCESS')) {
        $q.notify({ type: 'positive', message: '有新的任务完成啦~ 快去看看吧' })
      } else if (checkNewState(data, 'FAILED')) {
        $q.notify({ type: 'warning', message: '有新的任务失败了，快去检查下吧' })
      }
    }
    taskGeneratorData.value = (data ?? []).map(item => {
      const generatorItem = item as GeneratorType
      const file = generatorFile.value[item.id]

      if (file === undefined) {
        return generatorItem
      }
      generatorItem.chartTotal = file.chartTotal
      generatorItem.total = file.total
      generatorItem.dataTotal = file.dataTotal
      generatorItem.dirFiles = file.dirFiles
      return generatorItem
    })
  } finally {
    loading.table = false
    loading.refresh = false
    loading.count = false
  }
}

onMounted(() => {
  handleData()
  registerInterval(handleData, refreshTime.value * 1000)
})

watch(() => route.params.id, handleData)

const handleAdd = () => {
  $q.dialog({
    component: GeneratorEditDialog,
    componentProps: {
      taskId: taskId.value,
      item: null
    }
  }).onOk(handleData)
}

const handleCount = async () => {
  if (taskGeneratorData.value.length === 0 || !isElectron()) {
    return
  }
  loading.count = true
  const lastTaskId = _.cloneDeep(taskId.value)
  try {
    const data = taskGeneratorData.value
    const countData: Record<number, TableExtend> = {}
    for (const index in data) {
      if (!data[index].files) {
        continue
      }
      const fileList: string[] = data[index].files!.split(GENERATOR_FILE_SPLIT)
      let total = 0
      for (const fileIndex in fileList) {
        total += (await window.FileApi.getFileCount(fileList[fileIndex])).total
      }
      countData[data[index].id] = {}
      countData[data[index].id].dataTotal = total
      const dirFiles = window.FileApi.getApplicationDirectoryFiles(data[index].name)
      countData[data[index].id].chartTotal = dirFiles.length
      countData[data[index].id].dirFiles = dirFiles
      if (lastTaskId !== taskId.value) {
        return
      }
    }
    generatorFile.value = countData
  } finally {
    loading.count = false
  }
}

watch(generatorFile, () => {
  taskGeneratorData.value = (taskGeneratorData.value ?? []).map(generatorItem => {
    const file = generatorFile.value[generatorItem.id]
    if (file === undefined) {
      return generatorItem
    }
    generatorItem.chartTotal = file.chartTotal
    generatorItem.total = file.total
    generatorItem.dataTotal = file.dataTotal
    generatorItem.dirFiles = file.dirFiles
    return generatorItem
  })
})

const handleRun = (item: GeneratorType) => {
  const fileList = item.files!.split(GENERATOR_FILE_SPLIT)
  if (fileList.length === 0) {
    $q.notify({ type: 'warning', message: '没有可以处理的文件' })
    return
  }
  console.log(item.configObj)
  $q.dialog({
    component: GeneratorStartDialog,
    componentProps: {
      taskId: taskId.value,
      files: fileList,
      id: item.id,
      currentStatus: item.status,
      config: item.configObj
    }
  }).onOk(handleData)
}

const handleEdit = (row: GeneratorType) => {
  if (!row.files) {
    $q.notify({ type: 'negative', message: '当前数据不存在任何文件，似乎是错误数据' })
    return
  }
  $q.dialog({
    component: GeneratorEditDialog,
    componentProps: {
      item: row,
      taskId: taskId.value
    }
  }).onOk(async () => {
    await handleData()
  })
}

const handleDelete = (row: GeneratorType) => {
  $q.dialog({
    title: '确认移除吗',
    message: `此操作将会移除 ${row.name} 所有数据但不会移除已经生成的图表文件（如果已生成过）。`,
    cancel: { color: 'primary', outline: true },
    ok: { color: 'negative', outline: true }
  }).onOk(async () => {
    await client.DELETE('/task/{task_id}/generator/{generator_id}', {
      params: { path: { task_id: taskId.value!, generator_id: row.id } }
    })
    _.pull(taskGeneratorData.value, row)
  })
}

const handleShowOutput = (row: GeneratorType) => {
  generatorOutputDialog.value?.openDialog(taskId.value!, row.id)
}

const handleShowChart = (row: GeneratorType) => {
  showChartDialog.value?.openDialog(row)
}

const handleGeneratorBar = () => {
  generatorStartBarDialog.value?.openDialog(selected.value)
}

const handleAutoRefresh = (time: number) => {
  refreshTime.value = time
  if (time < 0) {
    removeInterval()
    return
  }
  registerInterval(handleData, time * 1000)
}

</script>

<template>
  <div class="container">
    <GeneratorOutputDialog ref="generatorOutputDialog" />
    <GeneratorStartBarDialog ref="generatorStartBarDialog" :task-id="taskId" />
    <ShowChartDialog ref="showChartDialog" />
    <q-table class="container-table container-table-sticky-head" v-model:selected="selected" flat bordered
      :rows="taskGeneratorData" selection="multiple" :columns="columns" row-key="id" :pagination="{ rowsPerPage: 10 }"
      :filter="filter" :loading="loading.table" table-header-class="sticky-head">
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td auto-width>
            <q-checkbox v-model="props.selected" color="primary" />
          </q-td>
          <q-td key="id" class="cursor-pointer" auto-width :props="props" @click="props.expand = !props.expand">
            {{ props.row.id }}
          </q-td>
          <q-td key="name" auto-width class="cursor-pointer ellipsis" style="max-width: 240px;" :props="props"
            @click="props.expand = !props.expand">
            {{ props.row.name }}
            <q-tooltip anchor="top middle" self="center middle">{{ props.row.name }}</q-tooltip>
          </q-td>
          <q-td key="status" auto-width :props="props">
            <q-chip v-if="props.row.status === 'WAITING'" color="ongoing" class="text-white" size="10px">等待开始</q-chip>
            <q-chip v-else-if="props.row.status === 'SUCCESS'" color="positive" class="text-white"
              size="10px">成功</q-chip>
            <q-chip v-else-if="props.row.status === 'FAILED'" color="negative" class="text-white"
              size="10px">失败</q-chip>
            <q-chip v-else-if="props.row.status === 'PROCESSING'" color="warning" class="text-white"
              size="10px">进行中</q-chip>
          </q-td>
          <q-td key="total" auto-width class="cursor-pointer" :props="props" @click="props.expand = !props.expand">
            {{ props.row.files && (props.row.files.split(GENERATOR_FILE_SPLIT).length ?? 0) }}
          </q-td>
          <q-td key="chartTotal" auto-width :props="props">
            <div class="cursor-pointer" @click="handleShowChart(props.row)">
              {{ props.row.chartTotal ?? '未加载' }}
            </div>
          </q-td>
          <q-td key="dataTotal" auto-width :props="props">
            {{ props.row.dataTotal ?? '未加载' }}
          </q-td>
          <q-td key="result" auto-width class="ellipsis" :props="props" style="max-width: 140px;">
            {{ props.row.result }}
            <q-tooltip anchor="top middle" self="center middle" max-width="400px">{{ props.row.result }}</q-tooltip>
          </q-td>
          <q-td key="action" auto-width :props="props">
            <q-btn flat round color="secondary" icon="play_circle" size="sm" dense @click="() => handleRun(props.row)">
              <q-tooltip anchor="top middle" self="center middle">开始生成</q-tooltip>
            </q-btn>
            <q-btn flat round color="primary" icon="terminal" size="sm" dense
              @click="() => handleShowOutput(props.row)">
              <q-tooltip anchor="top middle" self="center middle">任务日志</q-tooltip>
            </q-btn>
            <q-btn flat round color="primary" icon="folder" size="sm" dense
              @click="() => handleHomeDirectoryOpenFile(props.row.name)">
              <q-tooltip anchor="top middle" self="center middle">查看图表</q-tooltip>
            </q-btn>
            <q-btn flat round color="secondary" icon="edit" size="sm" dense @click="() => handleEdit(props.row)">
              <q-tooltip anchor="top middle" self="center middle">编辑</q-tooltip>
            </q-btn>
            <q-btn flat round color="red" icon="delete" size="sm" dense @click="() => handleDelete(props.row)">
              <q-tooltip anchor="top middle" self="center middle">删除</q-tooltip>
            </q-btn>
          </q-td>
        </q-tr>
        <q-tr v-show="props.expand" :props="props">
          <q-td colspan="100%">
            <template v-if="props.row.files && props.row.files.split(GENERATOR_FILE_SPLIT).length > 0">
              <template v-for="item in props.row.files.split(GENERATOR_FILE_SPLIT)" :key="item">
                <div class="text-no-wrap vertical-middle">
                  <q-btn flat round color="primary" icon="text_snippet" size="xs" dense
                    @click="() => handleOpenFile(item)" />
                  {{ item }}
                </div>
              </template>
            </template>
          </q-td>
        </q-tr>
      </template>
      <template v-slot:top>
        <q-input dense debounce="300" style="width: 20rem;" color="primary" v-model="filter" placeholder="输入名称进行搜索">
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
        <q-space />
        <div class="row q-gutter-md">
          <q-btn-dropdown color="primary" size="sm" outline :label="`自动刷新(${refreshTime > 0 ? refreshTime : '-'}s)`">
            <q-list>
              <q-item clickable v-close-popup @click="handleAutoRefresh(-1)">
                <q-item-section>
                  <q-item-label>不刷新</q-item-label>
                </q-item-section>
              </q-item>

              <q-item clickable v-close-popup @click="handleAutoRefresh(5)">
                <q-item-section>
                  <q-item-label>5 秒</q-item-label>
                </q-item-section>
              </q-item>

              <q-item clickable v-close-popup @click="handleAutoRefresh(10)">
                <q-item-section>
                  <q-item-label>10 秒</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
          <q-btn color="secondary" outline label="生成对比柱状图" :disable="selected.length < 1" @click="handleGeneratorBar"
            size="sm">
            <q-tooltip anchor="top middle" self="center middle">你需要先选择至少一行才可以进行进行此操作</q-tooltip>
          </q-btn>
          <q-btn color="primary" outline label="统计图表" :loading="loading.count" @click="handleCount" size="sm" />
          <q-btn color="primary" outline label="刷新" :loading="loading.refresh" @click="handleData" size="sm" />
          <q-btn color="primary" outline label="添加" @click="handleAdd" size="sm" />
        </div>
      </template>
    </q-table>
  </div>
</template>

<style scoped lang="scss">
.container-table {
  height: calc(100vh - 140px);
}
</style>
