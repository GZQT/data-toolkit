// noinspection NonAsciiCharacters,JSNonASCIINames

import { Report } from 'pages/report/report-store'
import fs from 'fs'
import { createReport } from 'docx-templates'
import path from 'path'
import xlsx from 'node-xlsx'
import { date, is } from 'quasar'
import _ from 'lodash'

const imageToBase64 = (filePath: string): string => {
  const imageBuffer = fs.readFileSync(filePath)
  return imageBuffer.toString('base64')
}

const checkReportPath = (report: Report) => {
  if (!fs.existsSync(report.templatePath)) {
    return Promise.reject(`模板文件不存在，路径 ${report.templatePath}`)
  }
  if (!fs.existsSync(report.chartPath)) {
    return Promise.reject(`图表目录不存在，路径 ${report.templatePath}`)
  }
  if (!fs.existsSync(report.outputPath)) {
    return Promise.reject(`输出目录不存在，路径 ${report.templatePath}`)
  }
  if (!fs.statSync(report.templatePath).isFile()) {
    return Promise.reject(`模板文件路径不是一个文件，路径 ${report.templatePath}`)
  }
  if (!fs.statSync(report.chartPath).isDirectory()) {
    return Promise.reject(`图表路径不是一个目录，路径 ${report.chartPath}`)
  }
  if (!fs.statSync(report.outputPath).isDirectory()) {
    return Promise.reject(`输出路径不是一个目录，路径 ${report.outputPath}`)
  }
  return null
}

const readDirRecursive = (dir: string, fileList: string[] = []): string[] => {
  const files = fs.readdirSync(dir)

  files.forEach(file => {
    const filePath = path.join(dir, file)
    const stat = fs.statSync(filePath)

    if (stat.isDirectory()) {
      readDirRecursive(filePath, fileList)
    } else {
      fileList.push(filePath)
    }
  })

  return fileList
}

const parseExcelFile = async (excelList: string[]) => {
  const data: Record<string, string> = {}
  for (const excelPath of excelList) {
    const workSheets = xlsx.parse(excelPath, { cellDates: true })
    let type = ''
    if (excelPath.includes('平均值')) {
      type = '平均值'
    } else if (excelPath.includes('原始值')) {
      type = '原始值'
    } else if (excelPath.includes('最大最小值')) {
      type = '最大最小值'
    } else if (excelPath.includes('均方根')) {
      type = '均方根'
    }
    const workSheet = workSheets[0]
    const rowData = workSheet.data
    rowData.forEach(item => {
      let key = item[0]
      if (key.includes(' ')) {
        key = key.split(' ')[0]
        data[`${key}_${type}_位置`] = key.split(' ')[1]
      } else {
        data[`${key}_${type}_位置`] = item[6] ?? ''
      }
      data[`${key}_${type}_最大值`] = item[1]
      data[`${key}_${type}_最大值时间`] = date.formatDate(item[2], 'YYYY-MM-DD HH:mm:ss')
      data[`${key}_${type}_最小值`] = item[3]
      data[`${key}_${type}_最小值时间`] = date.formatDate(item[4], 'YYYY-MM-DD HH:mm:ss')
      data[`${key}_${type}_变化量`] = item[5]
    })
  }
  return data
}

export const reportGenerate = async (report: Report): Promise<void> => {
  const check = checkReportPath(report)
  if (check !== null) {
    return check
  }
  const fileList = readDirRecursive(report.chartPath)
  const chartList = fileList.filter(item => item.endsWith('.png'))
  const excelList = fileList.filter(item => item.endsWith('.xlsx'))
  const excelData = await parseExcelFile(excelList)
  const excelKeys = Object.keys(excelData)
  const data = report.config?.reduce((acc: Record<string, string>, item) => {
    acc[item.key] = item.value
    return acc
  }, {})
  try {
    const template = fs.readFileSync(report.templatePath)
    const buffer = await createReport({
      template,
      data,
      additionalJsContext: {
        文件: (fileName: string, width: number = 6, height: number = 4) => {
          const chartPath = chartList.find(item => item.includes(fileName))
          if (!chartPath) {
            throw new Error(`找不到文件 ${fileName}`)
          }
          return {
            width,
            height,
            data: imageToBase64(chartPath),
            extension: '.png'
          }
        },
        表: (key: string, keep: number = 3) => {
          let value = excelData[key] ?? 'none'
          if (is.number(value)) {
            const num = parseFloat(value)
            value = num.toFixed(keep)
          }
          return `${value}`
        },
        取最大: (key: string, keep: number = 3) => {
          const compareData = excelKeys
            .filter(item => item.includes(key) && item.includes('最大值') && is.number(excelData[item]))
            .map((item: string) => ({
              编号: item.split('_')[0],
              数值: excelData[item],
              位置: excelData[`${key.split('_最大值')[0]}_位置`]
            }))
          const maxValue = _.maxBy(compareData, '数值')
          if (is.number(maxValue)) {
            return maxValue.toFixed(keep)
          }
          return maxValue
        },
        取最小: (key: string, keep: number = 3) => {
          const compareData = excelKeys
            .filter(item => item.includes(key) && item.includes('最小值') && is.number(excelData[item]))
            .map((item: string) => ({
              编号: item.split('_')[0],
              数值: excelData[item],
              位置: excelData[`${key.split('_最小值')[0]}_位置`]
            }))
          const minValue = _.minBy(compareData, '数值')
          if (is.number(minValue)) {
            return minValue.toFixed(keep)
          }
          return minValue
        }
      },
      cmdDelimiter: ['{{', '}}']
    })

    fs.writeFileSync(path.join(report.outputPath, `${report.name}.docx`), buffer)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (e: any) {
    console.error(e)
    if (Object.keys(e).includes('command')) {
      return Promise.reject(`命令 ${e.command} 处理失败`)
    } else if (e.message.includes('resource busy or locked')) {
      return Promise.reject(`需要关闭文件 ${e.message.split('\'')[1]} 后才能生成新的文件`)
    }
    return Promise.reject(e.message)
  }
}
