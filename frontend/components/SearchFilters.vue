<template>
  <USelectMenu
    class="w-72 lg:w-96 cold-uselectmenu"
    placeholder="All Types"
    size="xl"
    :options="types"
    v-model="selected"
    @update:modelValue="onFilterChange"
  />
</template>

<script setup lang="ts">
const types = ['All Types', 'Question']
const selected = ref(types[0])
// Emit the selected value to parent
const emit = defineEmits(['filter-changed'])

const onFilterChange = () => {
  emit('filter-changed', selected.value)
}
</script>
