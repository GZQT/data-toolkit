<script setup lang="ts">
import { client } from 'src/boot/request'
import { ref } from 'vue'

defineOptions({
  name: 'TaskPage'
})
const splitterModel = ref(15)

const handleRequest = async () => {
  const { data } = await client.GET('/')
  console.log(data)
}

</script>
<template>
  <q-page class="q-ma-lg">
    <div @click="handleRequest">request test</div>
    <q-card class="q-py-md">
      <q-splitter v-model="splitterModel" style="height: 250px">
        <template v-slot:before>
          <q-list dense padding class="rounded-borders text-primary">
            <q-item :to="'/task/test'" active-class="active-link" clickable v-ripple>test</q-item>
          </q-list>
        </template>
        <template v-slot:after>
          <div>
            <router-view />
          </div>
        </template>
      </q-splitter>
    </q-card>
  </q-page>
</template>

<style scoped lang="scss">
.active-link {
  color: red
}
</style>
