<template>
  <div class="fullscreen bg-blue text-white text-center q-pa-md flex flex-center">
    <div>
      <div style="font-size: 30vh">
        404
      </div>

      <div class="text-h2" style="opacity:.4">
        啊哦，你仿佛走到了一个死胡同，这里什么都没有...
      </div>

      <q-btn
        class="q-mt-xl"
        color="white"
        text-color="blue"
        unelevated
        to="/"
        label="返回主页"
        no-caps
      />
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: 'ErrorNotFound'
})
</script>
