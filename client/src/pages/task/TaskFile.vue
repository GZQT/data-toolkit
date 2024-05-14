<script setup lang="ts">
import _ from 'lodash'
import { QTableProps, date, useQuasar } from 'quasar'
import { client } from 'src/boot/request'
import { components } from 'src/types/api'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

interface EditItem {
  id: number | null
  name: string[]
}

const $q = useQuasar()
const route = useRoute()
const taskFileData = ref<(components['schemas']['TaskFileResponse'] & { total?: number, fileUpdatedDate?: Date })[]>([])
const editDialog = ref(false)
const editItem = ref<EditItem>({
  id: null,
  name: []
})
const taskId = ref<number>()
const filter = ref('')
const loading = reactive({
  table: false,
  dialog: false,
  refresh: false,
  row: false
})

const handleData = async () => {
  taskId.value = Number(route.params.id as string)
  try {
    loading.table = true
    loading.refresh = true
    const { data } = await client.GET('/task/{task_id}/file', {
      params: { path: { task_id: taskId.value } }
    })
    taskFileData.value = data ?? []
  } finally {
    loading.table = false
    loading.refresh = false
  }
}

onMounted(() => {
  handleData()
})

watch(() => route.params.id, handleData)

const isAdd = computed(() => {
  return editItem.value.id === null
})

const columns: QTableProps['columns'] = [
  { name: 'name', label: '文件路径', field: 'name', align: 'left', sortable: true },
  { name: 'total', label: '数据总数', field: 'total', align: 'left', sortable: true },
  { name: 'updateDate', label: '更新时间', field: 'updatedDate', align: 'left', sortable: true },
  { name: 'action', label: '操作', field: 'name', align: 'left' }
]

const handleAdd = () => {
  editDialog.value = true
  editItem.value = {
    id: null,
    name: []
  }
}

const handleEdit = (row: components['schemas']['TaskFileResponse'] & { total?: number }) => {
  editDialog.value = true
  editItem.value = {
    id: row.id,
    name: [row.name]
  }
}

const handleSelect = () => {
  window.FileApi.selectFiles(isAdd.value)
    .then((pathList) => {
      if (!pathList) {
        return
      }
      if (isAdd.value) {
        const names = editItem.value.name
        pathList.concat(names)
        editItem.value = {
          id: editItem.value.id,
          name: _.union(pathList)
        }
        return
      }
      editItem.value = {
        id: editItem.value.id,
        name: pathList
      }
    })
}

const handleDeleteFile = (item: string) => {
  if (!isAdd.value) {
    $q.notify({
      type: 'warning',
      message: '无法删除，编辑时至少保留一项'
    })
    return
  }
  $q.dialog({
    title: '确认移除吗',
    message: `当前文件： ${item}`,
    cancel: true
  }).onOk(() => {
    const names = _.cloneDeep(editItem.value.name)
    _.pull(names, item)
    editItem.value = {
      id: editItem.value.id,
      name: _.union(names)
    }
  })
}

const handleSave = async () => {
  if (!taskId.value) {
    $q.notify({
      type: 'warning',
      message: '操作失败，无法获取当前操作的任务信息'
    })
    return
  }
  if (editItem.value.name.length === 0) {
    return
  }
  loading.dialog = true
  try {
    if (isAdd.value) {
      await client.POST('/task/{task_id}/file', {
        params: { path: { task_id: taskId.value } },
        body: { names: editItem.value.name }
      })
    } else {
      await client.PUT('/task/{task_id}/file/{task_file_id}', {
        params: { path: { task_id: taskId.value, task_file_id: editItem.value.id! } },
        body: { name: editItem.value.name[0] }
      })
    }
  } finally {
    handleData()
    loading.dialog = false
  }
}

const handleDeleteItem = (item: components['schemas']['TaskFileResponse']) => {
  if (!taskId.value) {
    $q.notify({
      type: 'warning',
      message: '操作失败，无法获取当前操作的任务信息'
    })
    return
  }
  $q.dialog({
    title: '确认移除吗',
    message: `移除于 ${date.formatDate(item.createdDate, 'YYYY年MM月DD日HH点mm分ss秒')} 创建的数据 ${item.name}`,
    cancel: {
      color: 'primary'
    },
    ok: {
      color: 'negative'
    }
  }).onOk(async () => {
    await client.DELETE('/task/{task_id}/file/{task_file_id}', {
      params: { path: { task_id: taskId.value!, task_file_id: item.id } }
    })
    _.pull(taskFileData.value, item)
  })
}

const handleLoadCount = () => {
  if (loading.row) {
    return
  }
  loading.row = true
  const promiseList = []
  const data = _.cloneDeep(taskFileData.value)
  for (const index in data) {
    const promise = window.FileApi.getFileCount(data[index].name)
      .then(file => {
        data[index].total = file.total
        data[index].fileUpdatedDate = file.updatedDate
      })
    promiseList.push(promise)
  }
  Promise.all(promiseList)
    .then(() => { taskFileData.value = data })
    .finally(() => { loading.row = false })
}

const handleOpenFile = (file: string) => {
  window.FileApi.openFileDirectory(file)
}

</script>

<template>
  <div class="container">
    <q-table class="container-table" flat bordered :rows="taskFileData" :columns="columns" row-key="id"
      :pagination="{ rowsPerPage: 10 }" :filter="filter" :loading="loading.table">
      <template v-slot:header-cell-total="props">
        <q-th :props="props">
          {{ props.col.label }}
          <q-icon name="refresh" size="1.5em"
            :class="loading.row ? 'cursor-not-allowed animation-rotate' : 'cursor-pointer '" @click="handleLoadCount" />
        </q-th>
      </template>
      <template v-slot:header-cell-updateDate="props">
        <q-th :props="props">
          {{ props.col.label }}
          <q-icon name="refresh" size="1.5em"
            :class="loading.row ? 'cursor-not-allowed animation-rotate' : 'cursor-pointer '" @click="handleLoadCount" />
        </q-th>
      </template>
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td key="name" :props="props">
            {{ props.row.name }}
          </q-td>
          <q-td key="total" :props="props">
            {{ props.row.total }}
          </q-td>
          <q-td key="updateDate" :props="props">
            {{ date.formatDate(props.row.fileUpdatedDate, 'YYYY年MM月DD日HH点mm分ss秒') }}
          </q-td>
          <q-td key="action" :props="props">
            <q-btn flat round color="secondary" icon="edit" size="sm" dense @click="() => handleEdit(props.row)" />
            <q-btn flat round color="primary" icon="folder" size="sm" dense
              @click="() => handleOpenFile(props.row.name)" />
            <q-btn flat round color="red" icon="delete" size="sm" dense @click="() => handleDeleteItem(props.row)" />
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
          <q-btn color="primary" outline label="刷新" :loading="loading.refresh" @click="handleData" size="sm" />
          <q-btn color="primary" outline label="添加" @click="handleAdd" size="sm" />
        </div>
      </template>
    </q-table>

    <q-dialog v-model="editDialog">
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-subtitle1">
            {{ editItem.id ? '编辑文件' : '新增文件' }}
            <q-btn flat round icon="add" size="xs" dense @click="handleSelect" />
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div v-if="editItem.name.length === 0" class="text-tip cursor-pointer" @click="handleSelect">请选择至少一个文件</div>
          <q-list v-else dense class="text-left full-width">
            <q-item v-for="item in editItem.name" :key="item" clickable v-ripple @click="() => {
              if (editItem.id) {
                handleSelect()
              } else {
                handleDeleteFile(item)
              }
            }">
              <q-item-section>
                {{ item }}
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions :align="'right'" class="text-primary">
          <q-btn flat label="取消" v-close-popup @click="editDialog = false" />
          <q-btn flat :disable="editItem.name.length === 0" label="保存" :loading="loading.dialog" v-close-popup
            @click="handleSave" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
