import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import { date } from 'quasar'
import _ from 'lodash'

export interface BarConfig {
  chartName: string,
  xLabel: string,
  yLabel: string,
  xRotation: number,
  width: number
}

export const defaultConfig = {
  chartName: date.formatDate(Date.now(), 'YYYYMMDDHHmmss_') + '最大最小值对比图',
  xLabel: '测点',
  yLabel: '值',
  xRotation: 0,
  width: 0.35
}

export const useBarStore = defineStore('bar', () => {
  const barConfig = reactive<BarConfig>(_.cloneDeep(defaultConfig))
  const mainName = ref<string>('主')
  const changeMainName = (name: string) => {
    mainName.value = name
  }
  return {
    barConfig,
    mainName,
    changeMainName
  }
}, {
  persist: true
})
