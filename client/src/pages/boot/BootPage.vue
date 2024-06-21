<script setup lang="ts">
import Logo from 'src/assets/logo.png'
import { handleExitApp, isElectron } from 'src/utils/action'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const tip = ref('内核加载中...')
const router = useRouter()

onMounted(async () => {
  if (isElectron()) {
    const result = await window.KernelApi.start()
    if (result === true) {
      tip.value = '内核加载完成！'
      void router.push('/generator')
    } else {
      tip.value = result as string
    }
  }
})

</script>

<template>
  <div class="container row justify-center items-center">
    <q-btn dense class="q-ma-md absolute-top-right" rounded color="white" flat icon="close" @click="handleExitApp">
      <q-tooltip class="bg-white text-primary">关闭</q-tooltip>
    </q-btn>
    <div id="bg" class="row no-wrap justify-center items-center" style="width: 100%;height: 100%;color: white;">
      <img style="width:24vh;align-self: center;" alt="logo" :src="Logo" />
      <div class="q-ml-lg text-h4 text-grey-6 text-italic">贵州黔通工程技术有限公司</div>
    </div>
    <div style="position: absolute;bottom: 0;width: 100%;">
      <div style="position: absolute;height: 1px;background-color: #3b3e43;width: 100%;top:0"></div>
      <div id="progress"
        style="position: absolute;height: 1px;background-color: #d23f31;transition: width 50ms cubic-bezier(0, 0, 0.2, 1);top:0">
      </div>
      <div id="details"
        style="color: #9aa0a6;text-overflow: ellipsis;white-space: nowrap;overflow: hidden;padding: 8px;">
        {{ tip }}
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.container {
  height: 100vh;
  margin: 0;
  background: #1e1e1e;
  font-size: 12px;
  font-family: "Helvetica Neue", "Luxi Sans", "DejaVu Sans", "Hiragino Sans GB", "Microsoft Yahei", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", "Segoe UI Symbol", "Android Emoji", "EmojiSymbols";
}
</style>
