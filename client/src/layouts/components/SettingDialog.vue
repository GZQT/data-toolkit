<script setup lang="ts">
import { useDialogPluginComponent, useQuasar } from 'quasar'
import { handleBrowser, handleOpenExe, handleOpenHome } from 'src/utils/action'
import { useUpdateStore } from 'stores/update-store'
import { port } from 'boot/request'
import { useApplicationStore } from 'stores/application-store'
import { ref } from 'vue'
import { useRemoteServerStore } from 'stores/remote-server-store'

const $q = useQuasar()
const {
  dialogRef,
  onDialogHide,
  onDialogCancel
} = useDialogPluginComponent()

defineEmits([
  ...useDialogPluginComponent.emits
])

const restartLoading = ref(false)
const applicationStore = useApplicationStore()
const updateStore = useUpdateStore()
const remoteServerStore = useRemoteServerStore()

const handleUpdateTheme = (item: boolean | 'auto') => {
  $q.dark.set(item)
}

const handleRestartKernel = async () => {
  if (restartLoading.value) {
    return
  }
  $q.dialog({
    title: '确认进行重启内核吗？',
    cancel: { color: 'negative' },
    ok: { color: 'primary' }
  }).onOk(async () => {
    restartLoading.value = true
    try {
      await window.KernelApi.restartKernel()
      $q.notify({ message: '启动完成' })
    } catch (e) {
      $q.notify({ message: '启动失败 ' + e })
    } finally {
      restartLoading.value = false
    }
  })
}

</script>

<template>
  <div class="container">
    <q-dialog ref="dialogRef" @hide="onDialogHide" position="right" maximized>
      <q-card class="column full-height" style="width: 300px" data-cy="dialog-card">
        <q-card-section class="row">
          <div class="text-h6">设置</div>
          <q-space/>
          <q-btn flat round dense icon="close" @click="onDialogCancel"/>
        </q-card-section>
        <q-separator inset/>
        <q-card-section class="col q-pt-md column q-gutter-sm">
          <div class="row items-center">
            <div>主题：</div>
            <q-btn-toggle data-cy="theme-toggle" class="text-primary" size="12px" style="border: 1px solid" uno-caps
                          unelevated :model-value="$q.dark.mode" toggle-color="primary" :options="[
                { label: '明亮', value: false },
                { label: '系统', value: 'auto' },
                { label: '黑暗', value: true }
              ]" @update:model-value="handleUpdateTheme"/>
          </div>
          <div class="row items-center justify-between">
            <div>版本：{{ updateStore.data.version }}</div>
            <q-btn :disable="updateStore.newVersionIsDownloading" flat color="primary" size="md" dense
                   :loading="updateStore.data.loading" @click="() => updateStore.handleCheckUpdate(true)"
                   :label="updateStore.data.hasNewVersion ? `更新到 ${updateStore.data.newVersion} 版本`  : (updateStore.newVersionIsDownloading ? '正在下载更新' :`检查更新`)"
            >
              <q-badge style="margin-top: 2px" floating v-show="updateStore.data.hasNewVersion" color="red"
                       rounded></q-badge>
            </q-btn>
          </div>
          <div class="row items-center justify-between">
            内核端口：{{ port }}
            <div class="row items-center q-gutter-sm">
              <q-icon name="refresh"
                      :class="`q-ml-xs ${restartLoading?'cursor-not-allowed  animation-rotate':'cursor-pointer'}`"
                      @click="handleRestartKernel">
                <q-tooltip>重启内核</q-tooltip>
              </q-icon>
              <q-badge class="q-ml-xs cursor-pointer" @click="applicationStore.checkHealth" rounded
                       :color="applicationStore.status">
                <q-tooltip>{{ applicationStore.response }}</q-tooltip>
              </q-badge>
            </div>
          </div>
          <div class="row items-center justify-between">
            <div>
              远程地址：
              <span class="cursor-pointer">
                {{ remoteServerStore.remoteServer }}
                <q-popup-edit :model-value="remoteServerStore.remoteServer"
                              @update:model-value="remoteServerStore.handleUpdateRemoteServer" auto-save v-slot="scope">
                  <q-input v-model="scope.value" dense autofocus @keyup.enter="scope.set"/>
                </q-popup-edit>
              </span>
            </div>
            <q-badge class="q-ml-xs cursor-pointer" @click="remoteServerStore.checkHealth" rounded
                     :color="remoteServerStore.status">
              <q-tooltip>{{ remoteServerStore.response }}</q-tooltip>
            </q-badge>
          </div>
          <div class="q-mt-lg row text-primary items-center cursor-pointer "
               @click="handleBrowser('http://git-link.gzgswork.com:13000/gzgs-qtgc/data-toolkit')">
            <q-icon name="mdi-gitlab" class="q-mr-xs"/>
            <div class="link text-caption">查看源代码</div>
            <q-icon name="north_east" class="q-ml-xs" size="15px"/>
          </div>
          <div class="row text-primary items-center cursor-pointer "
               @click="handleBrowser('http://git-link.gzgswork.com:13000/gzgs-qtgc/data-toolkit/issues')">
            <q-icon name="mdi-bug" class="q-mr-xs"/>
            <div class="link text-caption">问题反馈</div>
            <q-icon name="north_east" class="q-ml-xs" size="15px"/>
          </div>
          <div class="row text-primary items-center cursor-pointer " @click="handleOpenHome">
            <q-icon name="control_camera" class="q-mr-xs" size="15px"/>
            <div class="link text-caption">打开应用文件路径</div>
            <q-icon name="north_east" class="q-ml-xs" size="15px"/>
          </div>
          <div class="row text-primary items-center cursor-pointer " @click="handleOpenExe">
            <q-icon name="home" class="q-mr-xs" size="15px"/>
            <div class="link text-caption">打开安装路径</div>
            <q-icon name="north_east" class="q-ml-xs" size="15px"/>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
