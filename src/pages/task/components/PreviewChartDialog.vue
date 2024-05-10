<script setup lang="ts">

import { useDialogPluginComponent } from 'quasar'
import { handleOpenFile } from 'src/utils/action'

defineProps<{
  file: string
}>()

defineEmits([
  ...useDialogPluginComponent.emits
])

const { dialogRef, onDialogHide, onDialogCancel } = useDialogPluginComponent()

const handleCancel = () => {
  onDialogCancel()
}
</script>

<template>

  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <div style="max-width: 1000px; width: 1000px;">
      <q-card class="q-dialog-plugin full-height full-width">
        <q-btn class="absolute" style="right: 0; z-index: 1;" round flat icon="close" @click="handleCancel()" />
        <q-card-section>
          <q-img :src="file.replace(/#/g, '%23').replace(/\s/g, '%20')"></q-img>
        </q-card-section>
      </q-card>
      <div class="text-white full-width text-center flex no-wrap items-center justify-center"
        style="height: 50px; background-color: rgba(0, 0, 0, 0.3);">
        {{ file }}
        <q-btn round flat icon="open_in_new" @click="handleOpenFile(file)" />
      </div>
    </div>
  </q-dialog>
</template>

<style scoped lang="scss"></style>
