import { components } from './api'

export interface GeneratorStartLineDialogForm {
  columnIndex: number[]
  timeRange: string
  xLabel: string
  yLabel: string
  xRotation: number
  name: string[]
  lineWidth: number
  fill: components['schemas']['ChartFillEnum'] | null,
  showGrid: boolean
}
