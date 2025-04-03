<template>
  <div>
    <USelectMenu
      class="lg:w-60 cold-uselectmenu"
      :class="{ 'non-all-selected': modelValue && !modelValue.startsWith('All') }"
      placeholder="All"
      size="lg"
      :options="options"
      :model-value="modelValue"
      @update:modelValue="emit('update:modelValue', $event)"
      searchable
    />
  </div>
</template>

<script setup>
defineProps({
  options: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: String,
    default: 'All',
  },
})

const emit = defineEmits(['update:modelValue'])
</script>
