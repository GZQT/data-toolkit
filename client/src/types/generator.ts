import { components } from './api'

export interface GeneratorStartLineDialogForm {
  chartColumnIndex: number[]
  chartTimeRange: string
  chartXLabel: string
  chartYLabel: string
  chartXRotation: number
  chartName: string[]
  chartLineWidth: number
  chartFill: components['schemas']['ChartFillEnum'] | null,
  chartShowGrid: boolean
}
