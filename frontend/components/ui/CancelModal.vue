<template>
  <UModal v-model="modelValueProxy" prevent-close>
    <slot name="cancel-modal" :close="closeModal">
      <div class="p-6 text-center">
        <h2 class="mb-4 text-lg font-bold">Discard changes?</h2>
        <p class="mb-6">
          Are you sure you want to cancel? All unsaved changes will be lost.
        </p>
        <div class="flex justify-center gap-4">
          <UButton color="gray" variant="outline" @click="closeModal"
            >Go Back</UButton
          >
          <UButton color="red" @click="onDiscard">Discard</UButton>
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
const emit = defineEmits(['update:modelValue', 'confirm-cancel'])

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

function onDiscard() {
  emit('confirm-cancel')
  closeModal()
}
</script>
