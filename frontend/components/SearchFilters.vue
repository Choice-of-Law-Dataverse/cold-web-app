<template>
  <USelectMenu
    class="w-72 lg:w-96 cold-uselectmenu"
    placeholder="All Types"
    size="xl"
    :options="types"
    :model-value="modelValue"
    @update:modelValue="emit('update:modelValue', $event)"
  />
</template>

<script setup lang="ts">
const types = ['All Types', 'Question']

defineProps({
  modelValue: {
    type: String,
    default: 'All Types',
  },
})

const emit = defineEmits(['update:modelValue'])
</script>
