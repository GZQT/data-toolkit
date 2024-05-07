<script setup lang="tsx">
import _ from 'lodash'
import { QChip, QTableProps, date, useQuasar } from 'quasar'
import { client } from 'src/boot/request'
import { components } from 'src/types/api'
import { handleHomeDirectoryOpenFile, handleOpenFile } from 'src/utils/action'
import { GENERATOR_FILE_SPLIT } from 'src/utils/constant'
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import FileSelectDialog from './components/FileSelectDialog.vue'
import GeneratorOutputDialog from './components/GeneratorOutputDialog.vue'
import GeneratorStartDialog from './components/GeneratorStartDialog.vue'

interface TableExtend {
  total?: number
  chartTotal?: number
  dataTotal?: number
}

const taskGeneratorData = ref<(components['schemas']['GeneratorResponse'] & TableExtend)[]>([])
const columns: QTableProps['columns'] = [
  { name: 'id', label: 'ID', field: 'id', align: 'left', sortable: true },
  { name: 'name', label: '批次', field: 'name', align: 'left', sortable: true },
  { name: 'status', label: '状态', field: 'status', align: 'left', sortable: true },
  { name: 'total', label: '文件数', field: 'total', align: 'left', sortable: true },
  { name: 'chartTotal', label: '图表数', field: 'total', align: 'left', sortable: true },
  { name: 'dataTotal', label: '数据行数', field: 'total', align: 'left', sortable: true },
  { name: 'result', label: '执行结果', field: 'result', align: 'left', sortable: true },
  { name: 'action', label: '操作', field: 'name', align: 'center' }
]

const $q = useQuasar()
const route = useRoute()
const taskId = ref<number>(0)
const fileSelectDialog = ref<null | InstanceType<typeof FileSelectDialog>>(null)
const generatorStartDialog = ref<null | InstanceType<typeof GeneratorStartDialog>>(null)
const generatorOutputDialog = ref<null | InstanceType<typeof GeneratorOutputDialog>>(null)
const filter = ref('')
const name = ref('')
const loading = reactive({
  table: false,
  refresh: false,
  count: false
})

const handleData = async () => {
  taskId.value = Number(route.params.id as string)
  try {
    loading.table = true
    loading.refresh = true
    const { data } = await client.GET('/task/{task_id}/generator', { params: { path: { task_id: taskId.value } } })
    taskGeneratorData.value = data ?? []
  } finally {
    loading.table = false
    loading.refresh = false
  }
  handleCount()
}

onMounted(() => {
  handleData()
})

const handleAdd = () => {
  fileSelectDialog.value?.openDialog(null, [])
  name.value = date.formatDate(Date.now(), 'YYYY年MM月DD日HH点mm分ss秒生成')
}

const handleFileSelect = async (id: number | null, files: string[]) => {
  if (name.value === '') {
    $q.notify({ type: 'warning', message: '操作失败: 名称必须填写' })
    return
  }
  if (files.length === 0) {
    $q.notify({ type: 'warning', message: '操作失败：未选择任何文件' })
    return
  }
  if (id === null) {
    await client.POST('/task/{task_id}/generator', {
      params: {
        path: { task_id: taskId.value }
      },
      body: {
        name: name.value,
        files: files.join(GENERATOR_FILE_SPLIT)
      }
    })
  } else {
    await client.PUT('/task/{task_id}/generator/{generator_id}', {
      params: {
        path: { task_id: taskId.value, generator_id: id }
      },
      body: {
        name: name.value,
        files: files.join(GENERATOR_FILE_SPLIT)
      }
    })
  }
  await handleData()
}

const handleCount = async () => {
  if (taskGeneratorData.value.length === 0) {
    return
  }
  loading.count = true
  try {
    const data = _.cloneDeep(taskGeneratorData.value)
    for (const index in data) {
      if (!data[index].files) {
        continue
      }
      const fileList: string[] = data[index].files!.split(GENERATOR_FILE_SPLIT)
      let total = 0
      for (const fileIndex in fileList) {
        total += (await window.FileApi.getFileCount(fileList[fileIndex])).total
      }
      data[index].dataTotal = total
      taskGeneratorData.value = data
      data[index].chartTotal = await window.FileApi.countFiles(data[index].name) ?? 0
    }
  } finally {
    loading.count = false
  }
}

const handleRun = (item: components['schemas']['GeneratorResponse'] & TableExtend) => {
  const fileList = item.files!.split(GENERATOR_FILE_SPLIT)
  if (fileList.length === 0) {
    $q.notify({ type: 'warning', message: '没有可以处理的文件' })
    return
  }
  generatorStartDialog.value?.openDialog(item.id, fileList, item.status!)
}

const handleEdit = (row: components['schemas']['GeneratorResponse'] & TableExtend) => {
  if (!row.files) {
    $q.notify({ type: 'negative', message: '当前数据不存在任何文件，似乎是错误数据' })
    return
  }
  fileSelectDialog.value?.openDialog(row.id, row.files.split(GENERATOR_FILE_SPLIT))
  name.value = row.name
}

const handleDelete = (row: components['schemas']['GeneratorResponse'] & TableExtend) => {
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

const handleShowOutput = (row: components['schemas']['GeneratorResponse'] & TableExtend) => {
  generatorOutputDialog.value?.openDialog(taskId.value!, row.id)
}

</script>

<template>
  <div class="container">
    <FileSelectDialog ref="fileSelectDialog" @save="handleFileSelect">
      <q-input class="q-mb-md" v-model="name" dense outlined placeholder="请输入生成名称" label="名称" />
    </FileSelectDialog>
    <GeneratorStartDialog ref="generatorStartDialog" :task-id="taskId" />
    <GeneratorOutputDialog ref="generatorOutputDialog" />
    <q-table class="container-table" flat bordered :rows="taskGeneratorData" :columns="columns" row-key="id"
      :pagination="{ rowsPerPage: 10 }" :filter="filter" :loading="loading.table" table-header-class="sticky-head">
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td key="id" class="cursor-pointer" :props="props" @click="props.expand = !props.expand">
            {{ props.row.id }}
          </q-td>
          <q-td key="name" class="cursor-pointer" :props="props" @click="props.expand = !props.expand">
            {{ props.row.name }}
          </q-td>
          <q-td key="status" :props="props">
            <q-chip v-if="props.row.status === 'WAITING'" color="ongoing" class="text-white" size="10px">等待开始</q-chip>
            <q-chip v-else-if="props.row.status === 'SUCCESS'" color="positive" class="text-white"
              size="10px">成功</q-chip>
            <q-chip v-else-if="props.row.status === 'FAILED'" color="negative" class="text-white"
              size="10px">失败</q-chip>
            <q-chip v-else-if="props.row.status === 'PROCESSING'" color="warning" class="text-white"
              size="10px">进行中</q-chip>
          </q-td>
          <q-td key="total" class="cursor-pointer" :props="props" @click="props.expand = !props.expand">
            {{ props.row.files && (props.row.files.split(GENERATOR_FILE_SPLIT).length ?? 0) }}
          </q-td>
          <q-td key="chartTotal" :props="props">
            {{ props.row.chartTotal }}
          </q-td>
          <q-td key="dataTotal" :props="props">
            {{ props.row.dataTotal }}
          </q-td>
          <q-td key="result" :props="props">
            {{ props.row.result }}
          </q-td>
          <q-td key="action" :props="props">
            <q-btn flat round color="secondary" icon="play_circle" size="sm" dense @click="() => handleRun(props.row)">
              <q-tooltip>开始生成</q-tooltip>
            </q-btn>
            <q-btn flat round color="primary" icon="terminal" size="sm" dense
              @click="() => handleShowOutput(props.row)">
              <q-tooltip>任务日志</q-tooltip>
            </q-btn>
            <q-btn flat round color="primary" icon="folder" size="sm" dense
              @click="() => handleHomeDirectoryOpenFile(props.row.name)">
              <q-tooltip>查看图表</q-tooltip>
            </q-btn>
            <q-btn flat round color="secondary" icon="edit" size="sm" dense @click="() => handleEdit(props.row)">
              <q-tooltip>编辑</q-tooltip>
            </q-btn>
            <q-btn flat round color="red" icon="delete" size="sm" dense @click="() => handleDelete(props.row)">
              <q-tooltip>删除</q-tooltip>
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
          <q-btn color="primary" outline label="加载计数" :loading="loading.count" @click="handleCount" size="sm" />
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
