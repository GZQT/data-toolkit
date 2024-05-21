<template>
  <q-btn data-cy="button" label="test emit" color="positive" rounded icon="edit" @click="$emit('test')" />
</template>

<script lang="ts" setup>

defineEmits({
  test: () => true
})
</script>
