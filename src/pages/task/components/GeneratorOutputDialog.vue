<script setup lang="ts">
import { ref } from 'vue'

const dialog = ref(false)
const output = ref('')

const openDialog = (str: string) => {
  output.value = str
  dialog.value = true
}

defineExpose({ openDialog })

</script>

<template>
  <div class="container">
    <q-dialog v-model="dialog" maximized position="right">
      <q-card style="width: 40rem;">
        <q-scroll-area class="q-pa-md" style="height: 100%; width: 100%;">
          <div class="text-no-wrap" v-for="(item, index) in output.split('\n')" :key="`row-${index}`">
            {{ item }}
          </div>
        </q-scroll-area>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss"></style>
