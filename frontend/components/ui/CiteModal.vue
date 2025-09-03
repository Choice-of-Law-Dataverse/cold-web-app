<template>
  <UModal
    :model-value="modelValue"
    @update:model-value="(v) => $emit('update:modelValue', v)"
  >
    <div class="p-4">
      <h3 class="text-lg font-semibold mb-2">Cite this entry</h3>
      <p class="text-sm text-gray-600">Citation details will appear here.</p>
    </div>
  </UModal>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
})
defineEmits(['update:modelValue'])
</script>
