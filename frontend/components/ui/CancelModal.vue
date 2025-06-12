<template>
  <UModal v-model="modelValueProxy" prevent-close>
    <slot name="cancel-modal" :close="closeModal">
      <div class="p-4">
        <Placeholder class="h-48" />
      </div>
    </slot>
  </UModal>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
})
const emit = defineEmits(['update:modelValue'])

const modelValueProxy = ref(props.modelValue)

watch(
  () => props.modelValue,
  (val) => {
    modelValueProxy.value = val
  }
)

watch(modelValueProxy, (val) => {
  emit('update:modelValue', val)
})

function closeModal() {
  modelValueProxy.value = false
}
</script>
