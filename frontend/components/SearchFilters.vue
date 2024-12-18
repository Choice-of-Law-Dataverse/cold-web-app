<template>
  <USelectMenu
    class="lg:w-60 cold-uselectmenu"
    placeholder="All Types"
    size="lg"
    :options="types"
    :model-value="modelValue"
    @update:modelValue="emit('update:modelValue', $event)"
  />
</template>

<script setup lang="ts">
const types = ['All Types', 'Court Decisions', 'Legal Instruments', 'Questions']

defineProps({
  modelValue: {
    type: String,
    default: 'All Types',
  },
})

const emit = defineEmits(['update:modelValue'])
</script>
