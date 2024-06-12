<script setup lang="ts">
import { useDialogPluginComponent, useQuasar } from 'quasar'
import { components } from 'src/types/remote-api'
import { onMounted, ref } from 'vue'
import _ from 'lodash'
import { remoteClient } from 'boot/request'

const {
  dialogRef,
  onDialogHide,
  onDialogOK,
  onDialogCancel
} = useDialogPluginComponent()

const props = defineProps<{
  dau?: components['schemas']['DauSearchResponse']
}>()

const defaultForm: components['schemas']['DauSearchResponse'] = {
  name: '',
  bridge: '',
  collectionStationNo: '',
  collectionDeviceNo: '',
  ipAddress: '',
  sampleRate: '',
  physicsChannel: '',
  installNo: '',
  transferNo: '',
  monitorProject: '',
  deviceType: '',
  manufacturer: '',
  specification: '',
  deviceNo: '',
  installLocation: '',
  direction: '',
  createdDate: null,
  updatedDate: null,
  id: null
}

const form = ref<components['schemas']['DauSearchResponse']>(_.cloneDeep(defaultForm))

onMounted(() => {
  if (props.dau) {
    form.value = _.cloneDeep(props.dau)
  }
})

defineEmits({
  ...useDialogPluginComponent.emits
})
const $q = useQuasar()

const handleSubmit = () => {
  if (!form.value.name) {
    $q.notify({
      type: 'warning',
      message: '桥梁名称是必填项哦~'
    })
    return
  }
  form.value.bridge = form.value.name
  if (form.value.id === null) {
    remoteClient.POST('/dau', {
      body: form.value
    }).then(() => {
      onDialogOK()
    })
  } else {
    remoteClient.PUT('/dau/{id}', {
      params: { path: { id: form.value.id } },
      body: form.value
    }).then(() => {
      onDialogOK()
    })
  }
}

</script>

<template>
  <q-dialog class="dau-update" ref="dialogRef" @hide="onDialogHide" position="right">
    <q-card class="q-dialog-plugin column full-height" style="max-height: 100%">
      <q-card-section class="q-pb-none flex row justify-between">
        <div class="text-h6">{{dau ? '编辑' : '添加'}}</div>
        <q-space/>
        <q-btn flat round size="sm" icon="close" @click="onDialogCancel"/>
      </q-card-section>
      <q-card-section class="flex column justify-between" style="flex: 1;">
        <q-scroll-area style="flex: 1;">
          <q-input v-model="form.name" label="桥梁名称" />
          <q-input v-model="form.collectionStationNo" label="采集仪编号" />
          <q-input v-model="form.collectionDeviceNo" label="采集设备编号" />
          <q-input v-model="form.ipAddress" label="IP地址" />
          <q-input v-model="form.sampleRate" label="采样率" />
          <q-input v-model="form.physicsChannel" label="物理通道" />
          <q-input v-model="form.installNo" label="安装点编号" />
          <q-input v-model="form.transferNo" label="传输编号" />
          <q-input v-model="form.monitorProject" label="监测项目" />
          <q-input v-model="form.deviceType" label="设备类型" />
          <q-input v-model="form.manufacturer" label="厂家名称" />
          <q-input v-model="form.specification" label="规格型号" />
          <q-input v-model="form.deviceNo" label="设备编号" />
          <q-input v-model="form.installLocation" label="安装位置" />
          <q-input v-model="form.direction" label="方向" />
        </q-scroll-area>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn color="negative" outline label="取消" @click="onDialogCancel" />
        <q-btn color="primary" outline label="保存" @click="handleSubmit" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<style scoped lang="scss">
.dau-update {
  &:deep(.q-dialog__inner) {
    padding: 0;
  }
}
</style>
