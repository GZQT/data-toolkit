import { defineStore } from 'pinia'
import { ref } from 'vue'
import { findDuplicates } from 'src/utils'
import { useQuasar } from 'quasar'

export interface MergeFile {
  fileObj?: File
  file?: string
  fileName?: string
  columns: string[]
  selectColumns: string[]
  loading: boolean
}

export const useMergeStore = defineStore('mergeStore', () => {
  const $q = useQuasar()
  const mergeData = ref<MergeFile[]>([
    { columns: [], selectColumns: [], loading: false }
  ])

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
      { columns: [], selectColumns: [], loading: false }
    )
  }

  const handleRemove = (index: number) => {
    console.log(index)
    mergeData.value.splice(index, 1)
  }

  return {
    mergeData,
    handleUpdateFile,
    handleAdd,
    handleRemove
  }
}, {
  persist: true
})
