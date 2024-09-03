<script setup lang="ts">
import _ from 'lodash'
import { useDialogPluginComponent, useQuasar } from 'quasar'
import { isElectron } from 'src/utils/action'
import { computed, onMounted, reactive, ref } from 'vue'
import GeneratorStartDauConfigDialog from 'pages/task/components/GeneratorStartDauConfigDialog.vue'
import { components } from 'src/types/api'
import { GeneratorType } from 'pages/task/TaskGenerator.vue'
import { client } from 'boot/request'
import { GENERATOR_FILE_SPLIT } from 'src/utils/constant'

interface EditItem {
  id: number | null
  fileList: string[]
}

const $q = useQuasar()
const {
  dialogRef,
  onDialogHide,
  onDialogOK,
  onDialogCancel
} = useDialogPluginComponent()
const editItem = reactive<components['schemas']['GeneratorCreateRequest'] & EditItem>({
  id: null,
  name: '',
  files: '',
  fileList: [],
  configObj: {
    converters: [],
    dauConfig: []
  }
})
const loading = ref(false)

defineEmits([
  // REQUIRED; need to specify some events that your
  // component will emit through useDialogPluginComponent()
  ...useDialogPluginComponent.emits
])

const isAdd = computed(() => {
  return editItem.id === null
})

const props = defineProps<{
  item: GeneratorType | null
  taskId: number
}>()

onMounted(() => {
  console.log('props.item', props.item)
  if (props.item === null) {
    editItem.id = null
    editItem.name = ''
    editItem.fileList = []
    editItem.configObj = {
      converters: [],
      dauConfig: []
    }
  } else {
    editItem.id = props.item.id
    editItem.name = props.item.name
    editItem.fileList = props.item.files?.split(GENERATOR_FILE_SPLIT) ?? []
    editItem.configObj = props.item.configObj
  }
})

// const emit = defineEmits<GeneratorEditEmit>()

const handleSelect = () => {
  if (!isElectron()) {
    return
  }
  window.FileApi.selectFiles(true)
    .then((pathList) => {
      if (!pathList) {
        return
      }
      const names = editItem.fileList
      editItem.fileList = _.union(_.concat(names, pathList))
    })
}

const handleDeleteFile = (item: string) => {
  if (!isAdd.value && editItem.fileList.length <= 1) {
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
    const names = _.cloneDeep(editItem.fileList)
    editItem.fileList = _.without(names, item)
  })
}

const handleSaveData = async () => {
  if (editItem.name.trim() === '') {
    $q.notify({
      type: 'warning',
      message: '操作失败: 名称必须填写'
    })
    return
  }
  if (editItem.fileList.length === 0) {
    $q.notify({
      type: 'warning',
      message: '操作失败：未选择任何文件'
    })
    return
  }
  if (editItem.id === null) {
    await client.POST('/task/{task_id}/generator', {
      params: {
        path: { task_id: props.taskId }
      },
      body: {
        name: editItem.name,
        files: editItem.fileList.join(GENERATOR_FILE_SPLIT),
        configObj: editItem.configObj
      }
    })
  } else {
    await client.PUT('/task/{task_id}/generator/{generator_id}', {
      params: {
        path: {
          task_id: props.taskId,
          generator_id: editItem.id
        }
      },
      body: {
        name: editItem.name,
        files: editItem.fileList.join(GENERATOR_FILE_SPLIT),
        configObj: editItem.configObj
      }
    })
  }
  onDialogOK()
}

const handleSave = async () => {
  console.log(editItem)
  if (editItem.fileList.length === 0) {
    return
  }
  loading.value = true
  try {
    await handleSaveData()
  } finally {
    loading.value = false
  }
}

const handleDauConfigDialog = async () => {
  if (editItem.fileList.length === 0) {
    $q.notify({
      message: '至少需要选择一个文件',
      type: 'warning'
    })
    return
  }
  const allColumns = (await window.FileApi.getCsvHeader(editItem.fileList[0])).filter(item => {
    return !item.includes('time') && !item.includes('id') && !item.includes('times') && !item.includes('col0')
  })
  $q.dialog({
    component: GeneratorStartDauConfigDialog,
    componentProps: {
      columns: allColumns,
      dauConfig: editItem.configObj?.dauConfig ?? []
    }
  }).onOk((config: components['schemas']['DauConfig'][]) => {
    editItem.configObj = {
      converters: editItem.configObj?.converters ?? [],
      dauConfig: config
    }
  })
}
</script>

<template>
  <div class="container">
    <q-dialog ref="dialogRef" @hide="onDialogHide">
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-subtitle1">
            {{ editItem.id ? '编辑文件' : '新增文件' }}
            <q-btn flat round icon="add" size="xs" dense @click="handleSelect"/>
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input class="q-mb-md" v-model="editItem.name" dense outlined placeholder="请输入生成名称" label="名称"/>
          <div v-if="editItem.fileList.length === 0" class="text-tip cursor-pointer" @click="handleSelect">
            请选择至少一个文件
          </div>
          <q-list v-else dense class="text-left full-width">
            <q-item-label>
              <q-item-section class="row">
                <div class="text-grey-6">
                  文件列表-{{ editItem.fileList.length }}（点击文件名称可以删除文件）
                </div>
              </q-item-section>
            </q-item-label>
            <q-item v-for="item in editItem.fileList" :key="item" clickable v-ripple @click="() => {
              if (editItem.id && editItem.fileList.length === 1) {
                $q.notify({ type: 'warning', message: '至少保留一个文件' })
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

        <q-card-actions class="text-primary row justify-between">
          <q-btn outline color="secondary" label="DAU 配置" @click="handleDauConfigDialog"/>
          <div>
            <q-btn outline color="red" label="取消" v-close-popup @click="onDialogCancel"/>
            <q-btn outline color="primary"
                   label="保存"
                   :disable="editItem.fileList.length === 0"
                   :loading="loading"
                   v-close-popup class="q-ml-md"
                   @click="handleSave"/>
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
