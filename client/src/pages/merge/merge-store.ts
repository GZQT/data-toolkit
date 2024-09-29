import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import { findDuplicates } from 'src/utils'
import { QFile, QSpinnerGears, useQuasar } from 'quasar'
import { client } from 'boot/request'
import { handleHomeDirectoryOpenFile } from 'src/utils/action'
import _ from 'lodash'

export interface MergeFile {
  fileObj?: File
  file?: string
  fileName?: string
  columns: string[]
  selectColumns: string[]
  loading: boolean
}

export interface Data {
  baseFilePath?: string
  baseColumn?: string
  loading: boolean
}

export const useMergeStore = defineStore('mergeStore', () => {
  const $q = useQuasar()
  const mergeData = ref<MergeFile[]>([
    {
      columns: [],
      selectColumns: [],
      loading: false
    }
  ])
  const data = reactive<Data>({
    loading: false
  })
  const selectFile = ref<QFile | undefined>()
  const mergeConfig = reactive({
    // 基准点数据为空时，移除此行
    removeBaseNull: true,
    // 合并数据时，这一行数据有一个为空时，移除此行
    removeNull: false
  })

  const handleUpdateFile = async (file: File, index: number) => {
    try {
      mergeData.value[index].loading = true
      mergeData.value[index].file = file.path
      mergeData.value[index].fileName = file.name
      mergeData.value[index].columns = await window.FileApi.getCsvHeader(file.path)
      mergeData.value[index].selectColumns = []
      const duplicates = findDuplicates(mergeData.value[index].columns)
      if (duplicates.length > 0) {
        $q.notify({
          type: 'warning',
          message: `${file.name} 文件中存在相同名称的列 ${duplicates}，处理时会存在错误，请更改一个再进行处理。`
        })
      }
    } finally {
      mergeData.value[index].loading = false
    }
  }

  const handleAdd = () => {
    mergeData.value.push(
      {
        columns: [],
        selectColumns: [],
        loading: false
      }
    )
  }

  const handleRemove = (index: number) => {
    console.log(index)
    mergeData.value.splice(index, 1)
  }

  const handleToBasePoint = (index: number, filePath?: string, column?: string) => {
    data.baseColumn = column
    data.baseFilePath = filePath
    if (column) {
      mergeData.value[index]?.selectColumns.push(column)
    }
  }

  const handleSubmit = () => {
    console.log('test')
    if (!data.baseFilePath || !data.baseColumn) {
      $q.notify({
        type: 'warning',
        message: '必须要选择一个基准点，你可以在列名称上右键设置基准点'
      })
      return
    }
    const dismiss = $q.notify({
      spinner: QSpinnerGears,
      message: '正在处理中...',
      timeout: 0
    })
    client.POST('/merge', {
      body: {
        base: {
          filePath: data.baseFilePath,
          column: data.baseColumn
        },
        config: {
          removeBaseNull: mergeConfig.removeBaseNull,
          removeNull: mergeConfig.removeNull
        },
        files: mergeData.value
          .filter(item => item.file && item.file.length > 0)
          .map(item => ({
            filePath: item.file!,
            selectColumns: _.uniq(item.selectColumns)
              .filter(column => (column !== data.baseColumn || data.baseFilePath !== item.file))
          }))
      }
    }).then(() => {
      $q.notify({
        type: 'success',
        message: '操作成功',
        timeout: 5000,
        actions: [
          {
            label: '好的',
            color: 'secondary',
            outline: true,
            handler: () => { /* ... */
            }
          },
          {
            label: '打开路径',
            color: 'white',
            outline: true,
            handler: () => {
              handleHomeDirectoryOpenFile('数据合并')
            }
          }
        ]
      })
    }).finally(() => {
      dismiss()
      data.loading = false
    })
  }

  return {
    data,
    mergeData,
    selectFile,
    mergeConfig,
    handleUpdateFile,
    handleAdd,
    handleRemove,
    handleToBasePoint,
    handleSubmit
  }
}, {
  persist: true
})
