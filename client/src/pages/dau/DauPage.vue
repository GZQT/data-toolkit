<script setup lang="ts">
import { QTableProps, useQuasar } from 'quasar'
import { computed, onMounted, reactive, ref } from 'vue'
import { remoteClient } from 'boot/request'
import { components } from 'src/types/remote-api'
import DauUpdateDialog from './DauUpdateDialog.vue'

const tableRef = ref()
const columns: QTableProps['columns'] = [
  {
    name: 'bridge',
    label: '桥梁名称',
    field: 'bridge',
    align: 'left',
    sortable: true
  },
  {
    name: 'collectionStationNo',
    label: '采集站编号',
    field: 'collectionStationNo',
    align: 'left',
    sortable: true
  },
  {
    name: 'collectionDeviceNo',
    label: '采集设备编号',
    field: 'collectionDeviceNo',
    align: 'left'
  },
  {
    name: 'physicsChannel',
    label: '物理通道',
    field: 'physicsChannel',
    align: 'left'
  },
  {
    name: 'ipAddress',
    label: 'IP 地址',
    field: 'ipAddress',
    align: 'left'
  },
  {
    name: 'sampleRate',
    label: '采样率',
    field: 'sampleRate',
    align: 'left'
  },
  {
    name: 'installNo',
    label: '安装点编号',
    field: 'installNo',
    align: 'left'
  },
  {
    name: 'action',
    label: '操作',
    field: 'action',
    align: 'center'
  }
]
const $q = useQuasar()
const dauData = ref<components['schemas']['DauSearchResponse'][]>([])
const form = reactive<{
  page: number, rowsPerPage: number, rowsNumber: number, loading: boolean, showCondition: boolean,
  condition: components['schemas']['DauSearchRequest']
}>({
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
  loading: false,
  showCondition: false,
  condition: {}
})

const handleData = async (page: number = 1, size: number = 10) => {
  form.loading = true
  try {
    const { data } = await remoteClient.GET('/dau', {
      params: {
        query: {
          page,
          size,
          ...form.condition
        }
      }
    })
    if (data) {
      dauData.value = data.items
      console.log(dauData.value)
      form.page = data.page ?? 0
      form.rowsPerPage = data.size ?? 0
      form.rowsNumber = data.total ?? 0
    }
  } finally {
    form.loading = false
  }
}

const handleTableRequest: QTableProps['onRequest'] = async ({ pagination }) => {
  const {
    page,
    rowsPerPage
  } = pagination
  await handleData(page, rowsPerPage)
}

const handleUpdatePagination: QTableProps['onUpdate:pagination'] = async (pagination) => {
  const {
    page,
    rowsPerPage
  } = pagination
  await handleData(page, rowsPerPage)
}

onMounted(async () => {
  await handleData()
})

const pagination = computed(() => {
  return {
    page: form.page,
    rowsPerPage: form.rowsPerPage,
    rowsNumber: form.rowsNumber
  }
})

const handleEdit = (row: components['schemas']['DauSearchResponse']) => {
  $q.dialog({
    component: DauUpdateDialog,
    componentProps: {
      dau: row
    }
  }).onOk(() => {
    handleData(form.page, form.rowsPerPage)
  })
}

const handleCopy = (row: components['schemas']['DauSearchResponse']) => {
  $q.dialog({
    component: DauUpdateDialog,
    componentProps: {
      dau: {
        ...row,
        id: null
      }
    }
  }).onOk(() => {
    handleData(form.page, form.rowsPerPage)
  })
}

const handleDelete = (row: components['schemas']['DauSearchResponse']) => {
  $q.dialog({
    title: '确认移除吗',
    message: `此操作将会移除 ${row.bridge} 所有数据但不会移除已经生成的图表文件（如果已生成过）。`,
    cancel: {
      color: 'primary',
      outline: true
    },
    ok: {
      color: 'negative',
      outline: true
    }
  }).onOk(() => {
    remoteClient.DELETE('/dau/{id}', {
      params: { path: { id: row.id! } }
    }).then(() => {
      handleData(form.page, form.rowsPerPage)
    })
  })
}

const handleReset = () => {
  form.condition = {}
  handleData(1, form.rowsPerPage)
}

const handleAdd = () => {
  $q.dialog({
    component: DauUpdateDialog,
    componentProps: {
      dau: undefined
    }
  }).onOk(() => {
    handleData(form.page, form.rowsPerPage)
  })
}

const conditionCount = computed(() => {
  let count = 0
  if (form.condition.ipAddress && form.condition.ipAddress.length > 0) {
    count++
  }
  if (form.condition.sampleRate && form.condition.sampleRate.length > 0) {
    count++
  }
  if (form.condition.physicsChannel && form.condition.physicsChannel.length > 0) {
    count++
  }
  if (form.condition.installNo && form.condition.installNo.length > 0) {
    count++
  }
  if (form.condition.transferNo && form.condition.transferNo.length > 0) {
    count++
  }
  if (form.condition.monitorProject && form.condition.monitorProject.length > 0) {
    count++
  }
  if (form.condition.deviceType && form.condition.deviceType.length > 0) {
    count++
  }
  if (form.condition.manufacturer && form.condition.manufacturer.length > 0) {
    count++
  }
  if (form.condition.specification && form.condition.specification.length > 0) {
    count++
  }
  if (form.condition.deviceNo && form.condition.deviceNo.length > 0) {
    count++
  }
  if (form.condition.installLocation && form.condition.installLocation.length > 0) {
    count++
  }
  if (form.condition.direction && form.condition.direction.length > 0) {
    count++
  }
  return count
})

</script>

<template>
  <div>
    <q-table
      ref="tableRef" class="main-table" :rows="dauData" :columns="columns" flat bordered
      row-key="id"
      :rows-per-page-options="[10,20,50]" :pagination="pagination" :loading="form.loading"
      @update:pagination="handleUpdatePagination"
      virtual-scroll
      :virtual-scroll-item-size="48"
      @request="handleTableRequest">
      <template v-slot:top>
        <div class="flex row full-width">
          <q-input class="col-4" dense outlined v-model="form.condition.bridge"
                   @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)"
                   label="桥梁名称"/>
          <q-input class="col-3 q-pl-md" dense outlined v-model="form.condition.collectionStationNo"
                   @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)"
                   label="采集仪编号"/>
          <q-input class="col-2 q-pl-md" dense outlined v-model="form.condition.collectionDeviceNo"
                   @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)"
                   label="采集设备编号"/>
          <div class="flex row items-center justify-end" style="flex: 1">
            <q-btn color="primary" :loading="form.loading" label="搜索" outline
                   @click="() => handleData(1, form.rowsPerPage)"/>
            <q-btn color="primary q-ml-md" label="重置" outline @click="handleReset"/>
            <q-btn color="secondary q-ml-md" label="添加" outline @click="handleAdd"/>
          </div>
          <q-expansion-item class="col-12" dense v-model="form.showCondition">
            <template v-slot:header>
              <div class="full-width flex justify-center items-center text-tip text-caption">
                <div>{{ form.showCondition ? '隐藏' : '显示' }}其他过滤条件</div>
                <q-badge v-if="conditionCount > 0" class="q-ml-sm" color="orange" text-color="white"
                         :label="conditionCount"/>
              </div>
            </template>
            <div class="flex row q-gutter-y-md">
              <q-input class="col-3" dense outlined v-model="form.condition.ipAddress" @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)" label="IP地址"/>
              <q-input class="col-3 q-pl-md" dense outlined v-model="form.condition.physicsChannel" @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)" label="物理通道"/>
              <q-input class="col-3 q-pl-md" dense outlined v-model="form.condition.installNo" @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)" label="安装点编号"/>
              <q-input class="col-3 q-pl-md" dense outlined v-model="form.condition.transferNo" @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)" label="传输编号"/>
              <q-input class="col-3" dense outlined v-model="form.condition.monitorProject" @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)" label="监测项目"/>
              <q-input class="col-3 q-pl-md" dense outlined v-model="form.condition.deviceType" @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)" label="设备类型"/>
              <q-input class="col-3 q-pl-md" dense outlined v-model="form.condition.manufacturer" @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)" label="厂家名称"/>
              <q-input class="col-3 q-pl-md" dense outlined v-model="form.condition.specification" @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)" label="规格型号"/>
              <q-input class="col-3" dense outlined v-model="form.condition.deviceNo" @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)" label="设备编号"/>
              <q-input class="col-3 q-pl-md" dense outlined v-model="form.condition.installLocation" @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)" label="安装位置"/>
              <q-input class="col-3 q-pl-md" dense outlined v-model="form.condition.direction" @keydown.enter.prevent="() => handleData(1, form.rowsPerPage)" label="方向"/>
            </div>
          </q-expansion-item>
        </div>
      </template>
      <template v-slot:body="props">
        <q-tr :props="props" @click="props.expand = !props.expand" class="cursor-pointer">
          <q-td key="bridge" :props="props">
            {{ props.row.bridge }}
          </q-td>
          <q-td key="collectionStationNo" :props="props">
            {{ props.row.collectionStationNo }}
          </q-td>
          <q-td key="collectionDeviceNo" :props="props">
            {{ props.row.collectionDeviceNo }}
          </q-td>
          <q-td key="physicsChannel" :props="props">
            {{ props.row.physicsChannel }}
          </q-td>
          <q-td key="ipAddress" :props="props">
            {{ props.row.ipAddress }}
          </q-td>
          <q-td key="sampleRate" :props="props">
            {{ props.row.sampleRate }}
          </q-td>
          <q-td key="installNo" :props="props">
            {{ props.row.installNo }}
          </q-td>
          <q-td key="action" :props="props" @click="(event: Event) => event.stopPropagation()">
            <q-btn flat round color="secondary" icon="edit" size="sm" dense @click="() => handleEdit(props.row)">
              <q-tooltip anchor="top middle" self="center middle">编辑</q-tooltip>
            </q-btn>
            <q-btn flat round color="primary" icon="content_copy" size="sm" dense @click="() => handleCopy(props.row)">
              <q-tooltip anchor="top middle" self="center middle">复制</q-tooltip>
            </q-btn>
            <q-btn flat round color="red" icon="delete" size="sm" dense @click="() => handleDelete(props.row)">
              <q-tooltip anchor="top middle" self="center middle">删除</q-tooltip>
            </q-btn>
          </q-td>
        </q-tr>
        <q-tr v-show="props.expand" :props="props">
          <q-td colspan="100%" class="content-bg">
            <div class="flex row q-col-gutter-xs">
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">桥梁名称:</div>
                <div>{{ props.row.bridge ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">采集仪编号:</div>
                <div>{{ props.row.collectionStationNo ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">采集设备编号:</div>
                <div>{{ props.row.collectionDeviceNo ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">IP地址:</div>
                <div>{{ props.row.ipAddress ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">采样率:</div>
                <div>{{ props.row.sampleRate ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">物理通道:</div>
                <div>{{ props.row.physicsChannel ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">安装点编号:</div>
                <div>{{ props.row.installNo ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">传输编号:</div>
                <div>{{ props.row.transferNo ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">监测项目:</div>
                <div>{{ props.row.monitorProject ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">设备类型:</div>
                <div>{{ props.row.deviceType ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">厂家名称:</div>
                <div>{{ props.row.manufacturer ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">规格型号:</div>
                <div>{{ props.row.specification ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">设备编号:</div>
                <div>{{ props.row.deviceNo ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">安装位置:</div>
                <div>{{ props.row.installLocation ?? '-' }}</div>
              </div>
              <div class="flex col-6 row">
                <div class="text-bold" style="width: 10rem">方向:</div>
                <div>{{ props.row.direction ?? '-' }}</div>
              </div>
            </div>
          </q-td>
        </q-tr>
      </template>
    </q-table>
  </div>
</template>

<style scoped lang="scss">
.main-table {
  max-height: calc(100vh - 80px);

  &:deep(.q-table) {
    thead {
      position: sticky;
      top: 0;
      @extend .sticky-head
    }
  }
}
</style>
