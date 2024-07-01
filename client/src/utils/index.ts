import _ from 'lodash'

export const isDataColumn = (col: string) => {
  return col !== 'id' && col !== 'col0' && col !== 'time' && !col.startsWith('Un')
}

export const findDuplicates = (arr: string[]): string[] => {
  const counts = _.countBy(arr)
  return _.keys(_.pickBy(counts, count => count > 1))
}
