<script setup lang="ts">
import { QTableProps, useQuasar } from 'quasar'
import { Report, useReportStore } from 'pages/report/report-store'
import ReportEditDialog from 'pages/report/ReportEditDialog.vue'
import { handleOpenDir, handleOpenFile } from 'src/utils/action'
import _ from 'lodash'

const $q = useQuasar()
const reportStore = useReportStore()
const columns: QTableProps['columns'] = [
  {
    name: 'name',
    label: '报告名称',
    field: 'name',
    align: 'left',
    sortable: true
  },
  {
    name: 'templatePath',
    label: '模板文件',
    field: 'templatePath',
    align: 'left'
  },
  {
    name: 'chartPath',
    label: '图表路径',
    field: 'chartPath',
    align: 'left'
  },
  {
    name: 'outputPath',
    label: '输出路径',
    field: 'outputPath',
    align: 'left'
  },
  {
    name: 'action',
    label: '操作',
    field: 'name',
    align: 'center'
  }
]
const handleAddData = () => {
  $q.dialog({
    component: ReportEditDialog
  })
}
const handleEdit = (row: Report) => {
  $q.dialog({
    component: ReportEditDialog,
    componentProps: {
      name: row.name
    }
  })
}
const handleDelete = (row: Report) => {
  $q.dialog({
    title: '确认删除吗？',
    message: '当前操作只会删除当前列表项，不会删除实际的任何文件',
    cancel: { color: 'primary', outline: true },
    ok: { color: 'negative', outline: true },
    focus: 'cancel'
  }).onOk(() => {
    const index = reportStore.data.reportList.findIndex(item => item.name === row.name)
    reportStore.data.reportList.splice(index, 1)
  })
}
const handleRun = (row: Report) => {
  $q.loading.show({
    delay: 60000,
    message: '正在生成中...'
  })
  window.ReportApi.generate(_.cloneDeep(row))
    .then(() => {
      $q.notify({
        message: '操作成功',
        icon: 'check_circle',
        actions: [
          {
            label: '查看',
            color: 'primary',
            handler: () => {
              handleOpenDir(row.outputPath + '/' + row.name + '.docx')
            }
          }
        ]
      })
    })
    .catch((e) => {
      $q.notify({
        type: 'negative',
        message: '操作失败 ' + e.message
      })
      console.error(e)
    })
    .finally(() => {
      $q.loading.hide()
    })
}
</script>

<template>
  <div>
    <q-table :rows="reportStore.data.reportList" :columns="columns" row-key="name" flat bordered :rows-per-page-options="[10,20,50]">
      <template v-slot:top>
        <div class="text-h6">报表生成</div>
        <q-icon class="q-ml-sm cursor-pointer" name="add" @click="handleAddData">
          <q-tooltip anchor="top middle" self="center middle">
            添加数据
          </q-tooltip>
        </q-icon>
        <q-space/>
        <q-input borderless dense placeholder="搜索" debounce="300" color="primary" v-model="reportStore.data.search">
          <template v-slot:append>
            <q-icon name="search"/>
          </template>
        </q-input>
      </template>
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td key="name" :props="props">
            {{ props.row.name }}
          </q-td>
          <q-td key="templatePath" :props="props" :class="(props.row.existTemplatePath ? 'cursor-pointer': 'text-red')" style="text-wrap: wrap"
                @click="() => props.row.existTemplatePath && handleOpenFile(props.row.templatePath)">
            {{ props.row.templatePath }}
          </q-td>
          <q-td key="chartPath" :props="props" :class="props.row.existChartPath ? 'cursor-pointer': 'text-red'" style="text-wrap: wrap"
                @click="() => props.row.existChartPath && handleOpenDir(props.row.chartPath)" >
            {{ props.row.chartPath }}
          </q-td>
          <q-td key="outputPath" :props="props" :class="props.row.existOutputPath ? 'cursor-pointer': 'text-red'" style="text-wrap: wrap"
                @click="() => props.row.existOutputPath && handleOpenDir(props.row.outputPath)">
            {{ props.row.outputPath }}
          </q-td>
          <q-td key="action" :props="props" auto-width>
            <q-btn flat round color="primary" icon="play_circle" size="sm" dense @click="() => handleRun(props.row)">
              <q-tooltip anchor="top middle" self="center middle">开始生成</q-tooltip>
            </q-btn>
            <q-btn flat round color="secondary" icon="edit" size="sm" dense @click="() => handleEdit(props.row)">
              <q-tooltip anchor="top middle" self="center middle">编辑</q-tooltip>
            </q-btn>
            <q-btn flat round color="red" icon="delete" size="sm" dense @click="() => handleDelete(props.row)">
              <q-tooltip anchor="top middle" self="center middle">删除</q-tooltip>
            </q-btn>
          </q-td>
        </q-tr>
      </template>
    </q-table>
  </div>
</template>

<style scoped lang="scss">

</style>
