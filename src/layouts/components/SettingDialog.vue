<script setup lang="ts">
import { useQuasar } from 'quasar'
import { handleBrowser } from 'src/utils/action'
import { ref } from 'vue'

const $q = useQuasar()
const version = process.env.APPLICATION_VERSION
const dialog = ref(false)

const openDialog = () => {
  console.log()

  dialog.value = true
}

defineExpose({
  openDialog
})

const handleUpdateTheme = (item: boolean | 'auto') => {
  $q.dark.set(item)
}

const handleOpenHome = () => {
  window.FileApi.openApplicationDirectory('')
}

</script>

<template>
  <div class="container">
    <q-dialog v-model="dialog" position="right" maximized>
      <q-card class="column full-height" style="width: 300px">
        <q-card-section class="row">
          <div class="text-h6">设置</div>
          <q-space />
          <q-btn flat round dense icon="close" @click="dialog = false" />
        </q-card-section>
        <q-separator inset />
        <q-card-section class="col q-pt-md column q-gutter-sm">
          <div> 版本：{{ version }} </div>
          <div class="row items-center">
            <div>主题：</div>
            <q-btn-toggle class="text-primary" size="12px" style="border: 1px solid" uno-caps unelevated
              :model-value="$q.dark.mode" toggle-color="primary" :options="[
                { label: '明亮', value: false },
                { label: '系统', value: 'auto' },
                { label: '黑暗', value: true }
              ]" @update:model-value="handleUpdateTheme" />
          </div>
          <div class="q-mt-lg row text-primary items-center cursor-pointer "
            @click="handleBrowser('http://36.134.229.254:1230/data/data-toolkit')">
            <q-icon name="mdi-gitlab" class="q-mr-xs" />
            <div class="link text-caption">查看源代码</div>
            <q-icon name="north_east" class="q-ml-xs" size="15px" />
          </div>
          <div class="row text-primary items-center cursor-pointer "
            @click="handleBrowser('http://36.134.229.254:1230/data/data-toolkit/-/issues')">
            <q-icon name="mdi-bug" class="q-mr-xs" />
            <div class="link text-caption">问题反馈</div>
            <q-icon name="north_east" class="q-ml-xs" size="15px" />
          </div>
          <div class="row text-primary items-center cursor-pointer " @click="handleOpenHome">
            <q-icon name="home" class="q-mr-xs" size="15px" />
            <div class="link text-caption">打开应用文件路径</div>
            <q-icon name="north_east" class="q-ml-xs" size="15px" />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
