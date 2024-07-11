import { defineStore } from 'pinia'
import { onMounted, reactive } from 'vue'
import { useInterval } from 'quasar'

export interface Report {
  name: string
  templatePath: string
  chartPath: string
  outputPath: string
  existTemplatePath?: boolean
  existChartPath?: boolean
  existOutputPath?: boolean
}

interface Data {
  reportList: Report[]
  search: string
}

export const useReportStore = defineStore('report', () => {
  const data = reactive<Data>({
    reportList: [],
    search: ''
  })
  const {
    registerInterval
  } = useInterval()
  const getFileStatus = () => {
    data.reportList = data.reportList.map((item) => {
      item.existTemplatePath = window.FileApi.checkExistPath(item.templatePath)
      item.existChartPath = window.FileApi.checkExistPath(item.chartPath)
      item.existOutputPath = window.FileApi.checkExistPath(item.outputPath)
      return item
    })
  }
  onMounted(() => {
    getFileStatus()
    registerInterval(() => {
      getFileStatus()
    }, 2000) // every 2 seconds
  })
  return {
    data,
    getFileStatus
  }
}, {
  persist: true
})
