<script setup lang="ts">

import { useDialogPluginComponent, useQuasar } from 'quasar'
import { computed, onMounted, reactive, watch } from 'vue'
import { remoteClient } from 'boot/request'
import { components as remoteComponents } from 'src/types/remote-api'
import { components } from 'src/types/api'
import _ from 'lodash'

const {
  dialogRef,
  onDialogHide,
  onDialogOK
} = useDialogPluginComponent()

defineEmits({
  ...useDialogPluginComponent.emits
})
const props = defineProps<{
  columns: string[],
  dauConfig?: components['schemas']['DauConfig'][]
}>()
const $q = useQuasar()
const dauBridge = reactive<{
  options: string[],
  loading: boolean,
  dauData: remoteComponents['schemas']['DauSearchResponse'][],
  dauLoading: boolean,
  isSelected: boolean
}>({
  options: [],
  loading: false,
  dauData: [],
  dauLoading: false,
  isSelected: false
})

type FormType = {
  dauBridge: string,
  currentItem: string,
  dauConfig: components['schemas']['DauConfig'][],
  condition: string,
  deviceCondition: string,
  splitter: number,
}

const form = reactive<FormType>({
  dauBridge: '',
  currentItem: '',
  dauConfig: [],
  condition: '',
  deviceCondition: '',
  splitter: 15
})

const handleDauBridge = () => {
  dauBridge.loading = true
  remoteClient.GET('/dau/bridge')
    .then((response) => {
      if (response.data) {
        dauBridge.options = response.data
      }
    })
    .finally(() => {
      dauBridge.loading = false
    })
}

const handleDauConfig = () => {
  dauBridge.dauLoading = true
  remoteClient.GET('/dau/bridge/{bridge_name}', {
    params: { path: { bridge_name: form.dauBridge } }
  }).then((response) => {
    if (response.data) {
      dauBridge.dauData = response.data
    }
  }).finally(() => {
    dauBridge.dauLoading = false
  })
}

onMounted(() => {
  handleDauBridge()
  if (props.dauConfig && props.dauConfig.length > 0) {
    form.dauConfig = props.dauConfig
    const ids = form.dauConfig.map(item => item.mapping)
    remoteClient.GET('/dau/ids', {
      params: { query: { ids } }
    }).then(response => {
      if (response.data) {
        dauBridge.dauData = response.data
      }
    })
  }
})

watch(() => form.dauBridge, (value) => {
  if (!value || value.trim() === '') {
    return
  }
  dauBridge.isSelected = true
  handleDauConfig()
})

const filterData = computed(() => {
  if (dauBridge.dauData.length === 0) {
    return []
  }
  return dauBridge.dauData.filter(item => {
    return (item.bridge?.includes(form.condition) || item.collectionDeviceNo?.includes(form.condition) ||
        item.collectionStationNo?.includes(form.condition) || item.physicsChannel?.includes(form.condition)) &&
      item.collectionDeviceNo?.includes(form.deviceCondition)
  })
})

watch(filterData, (value) => {
  if (value.length !== props.columns.length || !dauBridge.isSelected) {
    return
  }
  $q.notify({
    message: '当前选择的 DAU 配置数目与表格列数相同，是否自动进行一一匹配？这将会覆盖掉原来的配置项。',
    timeout: 0,
    actions: [
      {
        label: '不需要合并',
        color: 'secondary',
        outline: true,
        handler: () => {}
      },
      {
        label: '确认合并',
        outline: true,
        handler: () => {
          const list = _.sortBy(filterData.value, 'physicsChannel')
          console.log(list)
          form.dauConfig = props.columns.map((column, index) => ({
            column, mapping: filterData.value[index].id!
          }))
        }
      }
    ]
  })
})

const collectionDeviceNoOptions = computed(() => {
  return _.uniq(_.map(dauBridge.dauData, item => `${item.collectionDeviceNo}`))
})

const handleCheckItem = (item: remoteComponents['schemas']['DauSearchResponse'], value: boolean) => {
  const data = form.dauConfig.find(config => config.column === form.currentItem)
  if (data === undefined) {
    if (!value) {
      // 没有任何操作
      return
    }
    form.dauConfig.push({
      column: form.currentItem,
      mapping: item.id!
    })
    return
  }
  if (value) {
    data.mapping = item.id!
  } else {
    form.dauConfig.splice(form.dauConfig.indexOf(data))
  }
}

const handleSave = () => {
  onDialogOK(form.dauConfig)
}

const getItemMapping = (item: string) => {
  const find = form.dauConfig.find(config => config.column === item)
  if (!find) {
    return ''
  }
  const datum = dauBridge.dauData.find(datum => datum.id === find.mapping)
  if (datum) {
    return datum.installNo
  } else {
    return '已配置其他桥梁数据'
  }
}

</script>

<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" :maximized="true" transition-show="slide-up"
            transition-hide="slide-down">
    <q-card class="q-dialog-plugin flex column">
      <q-bar class="bg-primary text-white full-width fixed" style="z-index: 10;">
        <div>DAU 映射关系配置</div>
        <q-space/>
        <q-btn dense flat icon="close" v-close-popup>
          <q-tooltip>关闭</q-tooltip>
        </q-btn>
      </q-bar>
      <q-splitter
        class="full-height full-width flex row no-wrap q-pt-lg q-px-md"
        v-model="form.splitter"
        style="height: 250px"
      >
        <template v-slot:before>
          <q-list style="min-width: 16rem">
            <div class="text-caption text-tip q-pt-md">当前已读取到的列信息 {{ columns.length }}</div>
            <q-item class="flex items-center" :active="form.currentItem === item" v-ripple clickable dense
                    v-for="item in columns" :key="item" @click="() => {
                form.currentItem = item
              }">
              <q-badge class="q-mr-md" rounded
                       :color="form.dauConfig.find(config => config.column === item) !== undefined ? 'green' : 'yellow'"/>
              {{ item }} <q-badge class="q-ml-sm" v-if="form.dauConfig.find(config => config.column === item)" :label="`${getItemMapping(item)}`" />
            </q-item>
          </q-list>
        </template>
        <template v-slot:after>
          <div class="csv-column q-px-md full-height flex column no-wrap">
            <q-separator class="full-width"/>
            <q-select class="full-width q-mt-md" v-model="form.dauBridge" :options="dauBridge.options"
                      outlined :loading="dauBridge.loading" label="选择桥梁" dense/>
            <q-select class="full-width q-mt-sm" v-model="form.deviceCondition" :options="collectionDeviceNoOptions"
                      outlined :loading="dauBridge.loading" label="选择采集仪" dense/>
            <div class="text-tip full-width q-mt-sm flex items-center row justify-between">
              <div>{{ form.dauBridge }} 所有配置信息
                {{ dauBridge.dauLoading ? '加载数据中...' : dauBridge.dauData.length }}
              </div>
              <div class="flex flex-row q-gutter-x-md">
                <input v-model="form.condition" placeholder="输入需要搜索的关键字"/>
                <q-btn class="q-px-md" outline color="primary" dense label="保存" @click="handleSave" />
              </div>
            </div>
            <q-separator class="full-width q-mt-sm"/>
            <q-scroll-area class="fit q-py-md" :horizontal-thumb-style="{ 'opacity': '0' }">
              <q-list dense>
                <q-item v-if="filterData.length === 0">
                  <q-item-section>
                    <q-item-label>
                      暂无数据
                    </q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-for="item in filterData" dense tag="label" :key="`item-${item.id}`" v-ripple>
                  <q-item-section avatar>
                    <q-radio
                      dense
                      :model-value="form.dauConfig.find(config => config.column === form.currentItem && item.id === config.mapping) !== undefined"
                      :val="true"
                      @update:model-value="(value) => handleCheckItem(item, value)"
                    />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ item.collectionStationNo }} / {{ item.collectionDeviceNo }} /
                      <q-badge :label="`${item.physicsChannel}`"/>
                      /
                      <q-badge color="secondary" :label="`${item.installNo}`"/>
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-scroll-area>
          </div>
        </template>
      </q-splitter>
    </q-card>
  </q-dialog>
</template>

<style scoped lang="scss">

</style>
