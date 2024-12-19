<template>
  <div>
    <!-- <label class="block text-gray-700 text-sm mb-2">{{ label }}</label> -->
    <USelectMenu
      class="lg:w-60 cold-uselectmenu"
      placeholder="All"
      size="lg"
      :options="options"
      :model-value="modelValue"
      @update:modelValue="emit('update:modelValue', $event)"
      searchable
    />
  </div>
</template>

<script setup lang="ts">
defineProps({
  options: {
    type: Array as () => string[],
    required: true,
  },
  modelValue: {
    type: String,
    default: 'All',
  },
})

const emit = defineEmits(['update:modelValue'])
</script>
