<script setup lang="ts">
import { date, useDialogPluginComponent } from 'quasar'
import { reactive } from 'vue'

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

const form = reactive<{
  chartName: string,
  xLabel: string,
  yLabel: string,
  xRotation: number,
  width: number
}>({
  chartName: date.formatDate(Date.now(), 'YYYYMMDDHHmmss_') + '最大最小值对比图',
  xLabel: '测点',
  yLabel: '值',
  xRotation: -45,
  width: 0.35
})

const handleSubmit = () => {
  onDialogOK(form)
}

defineEmits({
  ...useDialogPluginComponent.emits
})

</script>

<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <q-card class="q-dialog-plugin">
      <q-card-section class="q-pb-none">
        <div class="text-h6">生成图表信息</div>
      </q-card-section>
      <q-card-section>
        <q-input v-model="form.chartName" label="图表标题" />
        <q-input v-model="form.xLabel" label="x 轴名称" />
        <q-input v-model="form.yLabel" label="y 轴名称" />
        <div>x 轴标签旋转角度 {{ form.xRotation }}</div>
        <q-slider v-model="form.xRotation" :min="-90" :max="90" :step="1" label color="primary" />
        <div>柱体宽度 {{ form.width }}</div>
        <q-slider v-model="form.width" :min="0.1" :max="1" :step="0.01" label color="primary" />
      </q-card-section>
      <q-card-actions :align="'right'">
        <q-btn outline color="primary" label="取消" @click="onDialogCancel" />
        <q-btn outline color="primary" label="确认" @click="handleSubmit" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>
<style scoped lang="scss"></style>
