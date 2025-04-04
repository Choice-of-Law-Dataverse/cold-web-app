<template>
  <div>
    <USelectMenu
      class="lg:w-60 cold-uselectmenu"
      :class="{ 'non-all-selected': modelValue && !modelValue.includes('All') }"
      :placeholder="options[0]"
      size="lg"
      :options="options"
      :model-value="modelValue"
      @update:modelValue="emit('update:modelValue', $event)"
      searchable
      selected-icon="i-material-symbols:circle"
      multiple
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
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue'])
</script>
