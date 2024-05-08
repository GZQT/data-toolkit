<script setup lang="ts">
import _ from 'lodash'
import { date, useQuasar } from 'quasar'
import { client } from 'src/boot/request'
import { GENERATOR_FILE_SPLIT, barStyle, thumbStyle } from 'src/utils/constant'
import { computed, ref } from 'vue'
import { GeneratorType } from '../TaskGenerator.vue'

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

const openDialog = async (list: GeneratorType[]) => {
  loading.value = true
  try {
    dialog.value = true
    data.value = list.filter(item => item.files !== null)
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

const handleSubmit = () => {
  $q.dialog({
    title: '输入图表名称',
    message: '生成出来的图表名称',
    prompt: { model: date.formatDate(Date.now(), 'YYYYMMDDHHmmss_') + '最大最小值对比图', type: 'text' },
    cancel: { outline: true },
    ok: { outline: true },
    persistent: true
  }).onOk(async name => {
    await client.POST('/task/{task_id}/generate/barChart', {
      params: { path: { task_id: props.taskId } },
      body: {
        chartName: name,
        compareGroup: compareGroup.value,
        generatorIds: data.value.map(item => item.id)
      }
    })
    dialog.value = false
  })
}

</script>

<template>
  <div class="container">
    <q-dialog v-model="dialog" persistent transition-show="flip-down" transition-hide="flip-up">
      <q-card class="column no-wrap" :style="{ width: data.length * 400 + 'px', maxWidth: '90vw' }">
        <q-bar class="bg-primary text-white">
          <div>生成柱状对比图</div>
          <q-icon v-if="loading" name="refresh" />
          <q-space />
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip>关闭</q-tooltip>
          </q-btn>
        </q-bar>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-tip text-caption">请在下方选择需要对比的数据列并进行添加</div>
          <q-space />
          <q-btn outline :disable="selectionCount < 2" color="secondary" size="sm" label="添加" @click="handleAdd">
            <q-tooltip v-if="selectionCount < 2">至少选择两列才可以进行此操作</q-tooltip>
          </q-btn>
          <q-btn outline :disable="compareGroup.length === 0" class="q-ml-md" color="primary" size="sm" label="完成"
            @click="handleSubmit">
            <q-tooltip v-if="compareGroup.length === 0">至少有一个对比组才可以进行此操作</q-tooltip>
          </q-btn>
        </q-card-section>
        <q-card-section class="q-my-none q-py-none row items-center" v-if="compareGroup.length > 0">
          <div>已选择</div>
          <q-chip removable class="q-ml-sm row" v-for="(item, index) in compareGroup" :key="`params-${index}`" dense
            @remove="handleRemoveResult(item)">
            <template v-for="(dataItem, dataIndex) in item" :key="`dataItem-${dataIndex}`">
              <div v-if="dataItem.length > 0">
                第{{ dataIndex }}表{{ dataItem.join() }}列
                <span v-if="dataIndex !== item.length - 1">对比&nbsp;</span>
              </div>
            </template>
          </q-chip>
        </q-card-section>

        <q-card-section class="q-mt-sm q-pt-none row q-gutter-lg" style="flex: 1;min-height: 400px;">
          <div v-for="(item, itemIndex) in data" :key="item.id" class="col q-mt-none">
            <div><b>{{ item.name }}</b> 所包含的列</div>
            <q-scroll-area :thumb-style="thumbStyle" :bar-style="barStyle" style="height: 500px;" class="q-mt-sm">
              <q-list bordered separator v-if="item.columns">
                <q-item dense v-for="(column, index) in item.columns" :key="column">
                  <q-item-section>
                    <q-checkbox dense v-model="selection[itemIndex]"
                      :disable="column === 'time' || column === 'col0' || column === 'id'" :val="index"
                      :label="`(${index}) ${column}`" />
                  </q-item-section>
                </q-item>
              </q-list>
            </q-scroll-area>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
