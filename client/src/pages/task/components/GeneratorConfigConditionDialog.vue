<script setup lang="ts">
import { useDialogPluginComponent } from 'quasar'
import { components } from 'src/types/api'
import { ref } from 'vue'
import dayjs from 'dayjs'

defineEmits([
  ...useDialogPluginComponent.emits
])

const condition = ref<components['schemas']['GeneratorDataCondition']>({
  type: 'MAX',
  value: 0,
  startTime: dayjs(new Date()).format('YYYY-MM-DD HH:mm:ss'),
  endTime: dayjs(new Date()).format('YYYY-MM-DD HH:mm:ss')
})

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

const options = [
  { label: '上限值', value: 'MAX' },
  { label: '下限值', value: 'MIN' }
]

const handleAdd = () => {
  onDialogOK(condition.value)
}
</script>

<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <q-card class="q-dialog-plugin" style="width: 400px; max-width: 80vw;">
      <q-form>
        <q-card-section class="flex items-center justify-between">
          <div class="text-h6">增加阈值</div>
          <q-btn dense flat rounded icon="close" v-close-popup/>
        </q-card-section>
        <q-card-section class="flex column q-gutter-y-md">
          <q-select outlined v-model="condition.type" :options="options" label="类型" :option-label="item => item.label" emit-value map-options :option-value="item => item.value"/>
          <q-input outlined v-model="condition.startTime" label="开始时间">
            <template v-slot:prepend>
              <q-icon name="event" class="cursor-pointer">
                <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                  <q-date v-model="condition.startTime" mask="YYYY-MM-DD HH:mm">
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="关闭" color="primary" flat />
                    </div>
                  </q-date>
                </q-popup-proxy>
              </q-icon>
            </template>
            <template v-slot:append>
              <q-icon name="access_time" class="cursor-pointer">
                <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                  <q-time v-model="condition.startTime" mask="YYYY-MM-DD HH:mm" format24h>
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="关闭" color="primary" flat />
                    </div>
                  </q-time>
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
          <q-input outlined v-model="condition.endTime" label="结束时间">
            <template v-slot:prepend>
              <q-icon name="event" class="cursor-pointer">
                <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                  <q-date v-model="condition.endTime" mask="YYYY-MM-DD HH:mm">
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="关闭" color="primary" flat />
                    </div>
                  </q-date>
                </q-popup-proxy>
              </q-icon>
            </template>
            <template v-slot:append>
              <q-icon name="access_time" class="cursor-pointer">
                <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                  <q-time v-model="condition.endTime" mask="YYYY-MM-DD HH:mm" format24h>
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="关闭" color="primary" flat />
                    </div>
                  </q-time>
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
          <q-input outlined v-model="condition.value" label="值" type="number" />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn color="primary" label="取消" @click="onDialogCancel" />
          <q-btn color="primary" label="添加" @click="handleAdd" />
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<style scoped lang="scss">

</style>
