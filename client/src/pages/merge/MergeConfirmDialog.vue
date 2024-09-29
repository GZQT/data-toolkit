<script setup lang="ts">

import { useDialogPluginComponent } from 'quasar'
import { useMergeStore } from 'pages/merge/merge-store'
import { onMounted } from 'vue'

const store = useMergeStore()
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

})

const handleSave = () => {
  store.handleSubmit()
  onDialogOK()
}

</script>

<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <q-card class="q-dialog-plugin">
      <q-card-section class="flex justify-between items-center">
        <div class="text-h6">合并配置</div>
        <q-btn flat round @click="onDialogCancel" icon="close"/>
      </q-card-section>
      <q-card-section class="flex column q-gutter-y-md">
        <q-toggle
          v-model="store.mergeConfig.removeBaseNull"
          dense
          checked-icon="check"
          color="red"
          label="基准点数据为空时，移除此行"
          unchecked-icon="clear"
        />
        <q-toggle
          v-model="store.mergeConfig.removeNull"
          dense
          checked-icon="check"
          color="red"
          label="合并数据有一个为空时，移除此行"
          unchecked-icon="clear"
        />
      </q-card-section>
      <q-card-actions align="right">
        <!--        <q-btn color="primary" label="OK" @click="onOKClick" />-->
        <q-btn color="red" outline label="取消" @click="onDialogCancel"/>
        <q-btn color="primary" outline label="保存" @click="handleSave"/>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<style scoped lang="scss">

</style>
