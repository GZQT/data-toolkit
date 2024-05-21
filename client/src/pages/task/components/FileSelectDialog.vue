<script setup lang="ts">
import _ from 'lodash'
import { useQuasar } from 'quasar'
import { isElectron } from 'src/utils/action'
import { computed, ref } from 'vue'

interface EditItem {
  id: number | null
  name: string[]
}

interface FileSelectEmit {
  (e: 'save', id: number | null, files: string[]): void
}

const $q = useQuasar()
const editDialog = ref(false)
const editItem = ref<EditItem>({
  id: null,
  name: []
})
const loading = ref(false)

const isAdd = computed(() => {
  return editItem.value.id === null
})

const openDialog = (id: number | null, files: string[]) => {
  editItem.value = {
    id, name: files
  }
  editDialog.value = true
}

defineExpose({ openDialog })

const emit = defineEmits<FileSelectEmit>()

const handleSelect = () => {
  if (!isElectron()) {
    return
  }
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
  if (!isAdd.value && editItem.value.name.length <= 1) {
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
  if (editItem.value.name.length === 0) {
    return
  }
  loading.value = true
  try {
    emit('save', editItem.value.id, editItem.value.name)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container">
    <q-dialog v-model="editDialog">
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-subtitle1">
            {{ editItem.id ? '编辑文件' : '新增文件' }}
            <q-btn flat round icon="add" size="xs" dense @click="handleSelect" />
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <slot></slot>
          <div v-if="editItem.name.length === 0" class="text-tip cursor-pointer" @click="handleSelect">请选择至少一个文件</div>
          <q-list v-else dense class="text-left full-width">
            <q-item-label>
              <q-item-section class="row">
                <div class="text-grey-6">
                  文件列表-{{ editItem.name.length }}（点击文件名称可以删除文件）
                </div>
              </q-item-section>
            </q-item-label>
            <q-item v-for="item in editItem.name" :key="item" clickable v-ripple @click="() => {
              if (editItem.id && editItem.name.length === 1) {
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

        <q-card-actions :align="'right'" class="text-primary">
          <q-btn flat label="取消" v-close-popup @click="editDialog = false" />
          <q-btn flat :disable="editItem.name.length === 0" label="保存" :loading="loading" v-close-popup
            @click="handleSave" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
