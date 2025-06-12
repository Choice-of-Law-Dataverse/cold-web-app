<template>
  <UModal v-model="modelValueProxy" prevent-close>
    <div class="p-6">
      <h2 class="text-lg font-bold mb-4 text-center">Ready to submit?</h2>
      <p class="mb-6 text-center">
        Please provide your contact information to complete the submission.
      </p>

      <!-- Email Field -->
      <UFormGroup
        size="lg"
        :error="saveModalErrors.email"
        class="mb-4"
        hint="Required"
      >
        <template #label>
          <span class="label">Email</span>
        </template>
        <UInput
          v-model="email"
          type="email"
          placeholder="Your email address"
          class="mt-2"
        />
      </UFormGroup>

      <!-- Comments Field -->
      <UFormGroup size="lg" class="mb-6">
        <template #label>
          <span class="label">Comments</span>
        </template>
        <UTextarea
          v-model="comments"
          placeholder="Optional comments about your submission"
          class="mt-2"
          :rows="3"
        />
      </UFormGroup>

      <div>
        <form @submit.prevent="onSubmit">
          <NuxtTurnstile ref="turnstile" v-model="token" />
        </form>
      </div>

      <div class="flex justify-center gap-4">
        <UButton color="primary" :disabled="!token" @click="handleSubmit"
          >Submit</UButton
        >
        <UButton color="gray" variant="outline" @click="closeModal"
          >Cancel</UButton
        >
      </div>
    </div>
  </UModal>
</template>

<script setup>
import { ref, watch, toRefs } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, required: true },
  email: { type: String, required: true },
  comments: { type: String, required: true },
  token: { type: String, required: true },
  saveModalErrors: { type: Object, required: true },
})
const emit = defineEmits([
  'update:modelValue',
  'update:email',
  'update:comments',
  'update:token',
  'submit',
])

const { email, comments, token, saveModalErrors } = toRefs(props)
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
function handleSubmit() {
  emit('submit')
}
</script>
