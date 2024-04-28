<template>
  <div>
    content {{ route.params.id }}
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

onMounted(() => {
  console.log(route)
})

defineOptions({
  name: 'TaskContent'
})

</script>
