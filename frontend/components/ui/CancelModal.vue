<template>
  <UModal v-model="modelValueProxy" prevent-close>
    <slot name="cancel-modal" :close="closeModal">
      <div class="p-6 text-center">
        <h2 class="text-lg font-bold mb-4">Discard changes?</h2>
        <p class="mb-6">
          33Are you sure you want to cancel? All unsaved changes will be lost.
        </p>
        <div class="flex justify-center gap-4">
          <UButton color="gray" variant="outline" @click="closeModal"
            >Go Back</UButton
          >
          <UButton color="red" @click="closeModal">Discard</UButton>
        </div>
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
