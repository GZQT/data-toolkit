<script setup lang="ts">
import _ from 'lodash'
import { QTableProps, date, useQuasar } from 'quasar'
import { client } from 'src/boot/request'
import { components } from 'src/types/api'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

interface EditItem {
  id: number | null
  name: string[]
}

const $q = useQuasar()
const route = useRoute()
const taskFileData = ref<components['schemas']['TaskFileResponse'][]>([])
const editDialog = ref(false)
const editItem = ref<EditItem>({
  id: null,
  name: []
})
const taskId = ref<number>()

const handleData = async () => {
  taskId.value = Number(route.params.id as string)
  const { data } = await client.GET('/task/{task_id}/file', {
    params: { path: { task_id: taskId.value } }
  })
  taskFileData.value = data ?? []
}

onMounted(() => {
  handleData()
})

watch(() => route.params.id, handleData)

const isAdd = computed(() => {
  return editItem.value.id === null
})

const columns: QTableProps['columns'] = [
  { name: 'name', label: '文件路径', field: 'name', align: 'left' },
  { name: 'total', label: '数据总数', field: 'total', align: 'left' },
  { name: 'updateDate', label: '更新时间', field: 'updateDate', align: 'left' },
  { name: 'action', label: '操作', field: 'name', align: 'left' }
]

const handleAdd = () => {
  editDialog.value = true
  editItem.value = {
    id: null,
    name: []
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
    cancel: true,
    persistent: true
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

</script>

<template>
  <div class="container">
    <q-table class="container-table" flat bordered :rows="taskFileData" :columns="columns" row-key="id"
      :pagination="{ rowsPerPage: 10 }">
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td key="name" :props="props">
            {{ props.row.name }}
          </q-td>
          <q-td key="total" :props="props">
            {{ props.row.total }}
          </q-td>
          <q-td key="updateDate" :props="props">
            {{ props.row.updateDate }}
          </q-td>
          <q-td key="action" :props="props">
            <q-btn flat round color="red" icon="delete" size="sm" dense @click="() => handleDeleteItem(props.row)" />
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <q-page-sticky position="bottom-right" :offset="[24, 24]">
      <q-btn fab size="xl" dense icon="add" color="primary" @click="handleAdd" />
    </q-page-sticky>

    <q-dialog v-model="editDialog" persistent>
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
            <q-item v-for="item in editItem.name" :key="item" clickable v-ripple @click="() => handleDeleteFile(item)">
              <q-item-section>
                {{ item }}
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions :align="'right'" class="text-primary">
          <q-btn flat label="取消" v-close-popup @click="editDialog = false" />
          <q-btn flat :disable="editItem.name.length === 0" label="保存" v-close-popup @click="handleSave" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
