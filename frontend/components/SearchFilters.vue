<template>
  <USelectMenu
    class="w-72 lg:w-96 cold-uselectmenu"
    placeholder="All Types"
    size="xl"
    :options="types"
    v-model="selected"
  />
</template>

<script setup lang="ts">
const types = ['All Types', 'Question']
const selected = ref(types[0])
</script>
