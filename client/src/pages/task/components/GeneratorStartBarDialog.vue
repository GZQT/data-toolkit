<script setup lang="tsx">
import _ from 'lodash'
import { useQuasar } from 'quasar'
import { client, remoteClient } from 'src/boot/request'
import { GENERATOR_FILE_SPLIT, barStyle, thumbStyle } from 'src/utils/constant'
import { computed, ref } from 'vue'
import { GeneratorType } from '../TaskGenerator.vue'
import GeneratorStartBarFormDialog from './GeneratorStartBarFormDialog.vue'
import { isElectron } from 'src/utils/action'
import { components } from 'src/types/remote-api'
import { BarConfig, useBarStore } from 'pages/task/components/bar-store.ts'

interface GeneratorColumns {
  columns?: string[]
}

const props = defineProps<{
  taskId: number
}>()

type GeneratorColumnsType = GeneratorType & GeneratorColumns
const $q = useQuasar()
const dialog = ref(false)
const data = ref<GeneratorColumnsType[]>([])
const loading = ref(false)
/**
 * 存放的是二维数组，第一个对应数据的索引，第二个对应列名的索引
 * [
 *   // 此时为 data 中索引为 0 的数组选择列，此时用户选择了1,2列
 *   [ 1, 2 ],
 *   // 此时为 data 中索引为 1 的数组选择列，此时用户选择了3,4列
 *   [ 3, 4 ]
 *   // 此时为 data 中索引为 2 的数组选择列，此时用户未进行选择
 *   [  ]
 * ]
 */
const selection = ref<number[][]>([])
const compareGroup = ref<number[][][]>([])
const dauList = ref<components['schemas']['DauSearchResponse'][]>([])
const barStore = useBarStore()

const getDauConfig = async (list: GeneratorType[]) => {
  if (list.length === 0) {
    dauList.value = []
    return
  }
  const dauConfigList = list.map(item => (item.configObj?.dauConfig) ?? [])
  const ids: number[] = _.uniq(_.map(_.flatten(dauConfigList), 'mapping'))
  const { data: dauData } = await remoteClient.GET('/dau/ids', {
    params: {
      query: {
        ids
      }
    }
  })
  dauList.value = dauData ?? []
}

const openDialog = async (list: GeneratorType[]) => {
  if (!isElectron()) {
    return
  }
  loading.value = true
  try {
    dialog.value = true
    const existData = list.filter(item => item.files !== null)
    data.value = existData
    barStore.changeMainName(existData[0].name)
    await getDauConfig(existData)
    const cloneData = _.cloneDeep(data.value)
    selection.value = []
    compareGroup.value = []
    for (const index in cloneData) {
      const files = cloneData[index].files!.split(GENERATOR_FILE_SPLIT)
      const file = files[0]
      const columns = await window.FileApi.getCsvHeader(file)
      cloneData[index].columns = columns
      selection.value.push([])
    }
    data.value = cloneData
  } finally {
    loading.value = false
  }
}

defineExpose({
  openDialog
})

const selectionCount = computed(() => {
  let count = 0
  for (const items of selection.value) {
    count += items.length
  }
  return count
})

const handleAdd = () => {
  compareGroup.value.push(selection.value)
  selection.value = []
  data.value.forEach(() => {
    selection.value.push([])
  })
}

const handleRemoveResult = (item: number[][]) => {
  _.pull(compareGroup.value, item)
}

const handleConfig = () => {
  $q.dialog({
    component: GeneratorStartBarFormDialog,
    componentProps: {
      config: barStore.barConfig
    }
  }).onOk(async (form: BarConfig) => {
    barStore.barConfig.chartName = form.chartName
    barStore.barConfig.xLabel = form.xLabel
    barStore.barConfig.yLabel = form.yLabel
    barStore.barConfig.xRotation = form.xRotation
    barStore.barConfig.width = form.width
  })
}

const handleSubmit = async () => {
  await client.POST('/task/{task_id}/generate/barChart', {
    params: { path: { task_id: props.taskId } },
    body: {
      compareGroup: compareGroup.value,
      generatorIds: data.value.map(item => item.id),
      ...barStore.barConfig
    }
  })
  dialog.value = false
}

const getDauInstallNo = (item: GeneratorColumnsType, column: string) => {
  if (!item.configObj?.dauConfig) {
    return ''
  }
  const dauConfig = item.configObj.dauConfig
  const exist = dauConfig.find(dau => dau.column === column)
  if (!exist) {
    return ''
  }
  const existDau = dauList.value.find(item => item.id === exist.mapping)
  if (!existDau) {
    return column
  }
  return existDau.installNo
}

const namesList = ['梁端位移监测统计柱状图', '支座位移监测统计柱状图', '左幅挠度最值统计柱状图', '右幅挠度最值统计柱状图', '墩顶位移监测统计柱状图', '结构应变统计柱状图', '结构裂缝统计柱状图']

const handleName = (name: string) => {
  barStore.barConfig.chartName = `${barStore.mainName}_${name}`
}
</script>

<template>
  <div class="container">
    <q-dialog v-model="dialog" class="full-height">
      <q-card class="column no-wrap full-height" :style="{ width: data.length * 400 + 'px', maxWidth: '90vw' }">
        <q-bar class="bg-primary text-white">
          <div>生成柱状对比图</div>
          <q-icon v-if="loading" name="refresh"/>
          <q-space/>
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip>关闭</q-tooltip>
          </q-btn>
        </q-bar>
        <q-card-section class="row items-center q-py-none flex justify-between">
          <q-input class="full-width" :model-value="barStore.barConfig.chartName" @update:model-value="e => {
            barStore.barConfig.chartName = `${e ?? ''}`
          }" borderless dense/>
        </q-card-section>
        <q-card-section class="q-py-none">
          <q-scroll-area :thumb-style="thumbStyle" :bar-style="barStyle" style="width: 200px;height: 40px"  class="full-width">
            <div class="row items-center q-py-none flex q-gutter-sm no-wrap ">
              <q-chip v-for="name in namesList" :key="name" dense outline square color="primary" clickable @click="() => handleName(name)">{{name}}</q-chip>
            </div>
          </q-scroll-area>
        </q-card-section>
        <q-card-section class="q-mt-sm q-py-none row q-gutter-lg" style="flex: 1">
          <div v-for="(item, itemIndex) in data" :key="item.id" class="col q-mt-none q-mb-lg">
            <div><b>{{ item.name }}</b> 所包含的列
              <q-icon v-if="barStore.mainName === item.name" color="warning" name="star" />
              <q-icon v-else name="star_outlined" class="q-ml-sm cursor-pointer" @click="() => barStore.changeMainName(item.name)" />
            </div>
            <q-scroll-area :thumb-style="thumbStyle" :bar-style="barStyle"
                           style="flex:1;height: 100%;min-height: 200px;max-height: 1500px" class="q-mt-sm">
              <q-list bordered separator v-if="item.columns">
                <q-item :dense="true" v-for="(column, index) in item.columns" :key="column">
                  <q-item-section>
                    <q-checkbox
                      dense v-model="selection[itemIndex]"
                      :disable="column === 'time' || column === 'col0' || column === 'id'" :val="index"
                      :label="`(${column}) ${getDauInstallNo(item, column)}`"/>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-scroll-area>
          </div>
        </q-card-section>
        <q-separator />
        <q-card-section class="q-mt-sm q-py-none row items-center" v-if="compareGroup.length > 0">
          <div>已选择</div>
          <q-chip :removable="true" class="q-ml-sm row" v-for="(item, index) in compareGroup" :key="`params-${index}`"
                  :dense="true" @remove="handleRemoveResult(item)">
            <template v-for="(dataItem, dataIndex) in item" :key="`dataItem-${dataIndex}`">
              <div v-if="dataItem.length > 0">
                第{{ dataIndex + 1 }}表{{ dataItem.join() }}列
                <span v-if="dataIndex !== item.length - 1">对比&nbsp;</span>
              </div>
            </template>
          </q-chip>
        </q-card-section>

        <q-card-actions>
          <q-btn outline :disable="selectionCount < 1" color="secondary" size="sm" label="添加" @click="handleAdd">
            <q-tooltip v-if="selectionCount < 2">至少选择两列才可以进行此操作</q-tooltip>
          </q-btn>
          <q-btn outline flat round size="sm" color="primary" icon="settings" class="q-mr-sm" @click="handleConfig"/>
          <q-space/>
          <q-btn outline :disable="compareGroup.length === 0" class="q-ml-md" color="primary" size="sm" label="完成"
                 @click="handleSubmit">
            <q-tooltip v-if="compareGroup.length === 0">至少有一个对比组才可以进行此操作</q-tooltip>
          </q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
