<script setup lang="ts">
import { useDialogPluginComponent } from 'quasar'
import { onMounted, reactive } from 'vue'
import { Report, useReportStore } from 'pages/report/report-store'
import _ from 'lodash'

const reportStore = useReportStore()
const props = defineProps<{
  name?: string
}>()
const data = reactive<Report>({
  name: '',
  templatePath: '',
  chartPath: '',
  outputPath: '',
  config: []
})

defineEmits([
  ...useDialogPluginComponent.emits
])

const {
  dialogRef,
  onDialogHide,
  onDialogOK,
  onDialogCancel
} = useDialogPluginComponent()
onMounted(() => {
  if (props.name) {
    const item = reportStore.data.reportList.find(item => item.name === props.name)
    data.name = item!.name
    data.templatePath = item!.templatePath
    data.chartPath = item!.chartPath
    data.outputPath = item!.outputPath
    data.config = _.cloneDeep(item!.config ?? [
      { key: '', value: '' }
    ])
  }
})
const handleSave = () => {
  data.config = data.config?.filter(item => item.key !== '')
  if (props.name) {
    reportStore.data.reportList = reportStore.data.reportList.map(item => item.name === props.name ? data : item)
  } else {
    reportStore.data.reportList.push(data)
  }
  reportStore.getFileStatus()
  onDialogOK()
}

const handlePickTemplatePath = async () => {
  const filePathList = await window.FileApi.selectFiles(false, false, [
    {
      name: 'Word Documents',
      extensions: ['doc', 'docx']
    }
  ])
  if (filePathList && filePathList.length > 0) {
    data.templatePath = filePathList[0]
  }
}
const handlePickChartPath = async () => {
  const filePathList = await window.FileApi.selectFiles(false, true, [])
  if (filePathList && filePathList.length > 0) {
    data.chartPath = filePathList[0]
  }
}
const handlePickOutputPath = async () => {
  const filePathList = await window.FileApi.selectFiles(false, true, [])
  if (filePathList && filePathList.length > 0) {
    data.outputPath = filePathList[0]
  }
}

const validateName = (val?: string) => {
  if (!val || val.length <= 0) {
    return '报告名称必须填写'
  }
  if (props.name) {
    return true
  }
  return reportStore.data.reportList.find(item => item.name === props.name) ? '当前名称已经存在' : true
}
const validateFileExist = (val?: string) => {
  if (!val || val.length <= 0) {
    return '此项是必填项'
  }
  return window.FileApi.checkExistPath(val) ? true : '路径不存在，请重新选择。'
}
const handleAddConfig = () => {
  data.config?.push({ key: '', value: '' })
}
const handleRemoveConfig = (index: number) => {
  data.config?.splice(index, 1)
}
</script>

<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <q-card class="q-dialog-plugin">
      <q-form
        @submit="handleSave">
        <q-card-section class="flex items-center">
          <div class="text-subtitle1">{{ name ? '编辑' : '添加' }}数据</div>
          <q-space/>
          <q-btn flat size="xs" v-close-popup round icon="close"/>
        </q-card-section>
        <q-card-section class="column q-gutter-y-xs">
          <q-input v-model="data.name" label="报告名称" outlined dense
                   lazy-rules
                   :rules="[ val => validateName(val)]"/>
          <q-input :model-value="data.templatePath" readonly label="模板路径" outlined dense
                   lazy-rules
                   :rules="[ val => validateFileExist(val)]"
                   @click="handlePickTemplatePath"/>
          <q-input :model-value="data.chartPath" readonly label="图表文件夹路径" outlined dense
                   lazy-rules
                   :rules="[ val => validateFileExist(val)]"
                   @click="handlePickChartPath"/>
          <q-input :model-value="data.outputPath" readonly label="输出路径" outlined dense
                   lazy-rules
                   :rules="[ val => validateFileExist(val)]"
                   @click="handlePickOutputPath"/>
          <div>模板变量<q-icon class="text-tip cursor-pointer q-ml-sm" size="xs" name="add_circle" @click="handleAddConfig"/></div>
          <div v-for="(item, index) in data.config" :key="`${index}-${item.key}-config`" class="row q-mt-md q-gutter-x-md items-center">
            <q-input :model-value="item.key" @change="(e: string) => {item.key = e}" label="键" outlined dense style="width: 40%"/>
            <q-input :model-value="item.value" @change="(e: string) => {item.value = e}" label="值" outlined dense style="width: 40%"/>
            <q-icon class="text-tip cursor-pointer" size="xs" name="do_not_disturb_on" @click="() => handleRemoveConfig(index)"/>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn color="primary" outline label="取消" @click="onDialogCancel"/>
          <q-btn color="primary" outline type="submit" label="保存"/>
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<style scoped lang="scss">

</style>
