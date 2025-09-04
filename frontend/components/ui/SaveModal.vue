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
        :error="saveModalErrorsProxy.submitter_email"
        class="mb-4"
        hint="Required"
      >
        <template #label>
          <span class="label">Email</span>
        </template>
        <UInput
          v-model="emailProxy"
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
          v-model="commentsProxy"
          placeholder="Optional comments about your submission"
          class="mt-2"
          :rows="3"
        />
      </UFormGroup>

      <div>
        <form @submit.prevent="onSubmit">
          <NuxtTurnstile ref="turnstile" v-model="tokenProxy" />
        </form>
      </div>

      <div class="flex justify-center gap-4">
        <UButton color="primary" :disabled="!tokenProxy" @click="handleSubmit"
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
import { ref, watch } from 'vue'
import { z } from 'zod'
import { useRouter } from '#imports'

const props = defineProps({
  modelValue: { type: Boolean, required: true },
  email: { type: String, required: true },
  comments: { type: String, required: true },
  token: { type: String, required: true },
  saveModalErrors: { type: Object, required: true },
  name: { type: String, required: true },
  specialists: { type: Array, required: true },
  date: { type: [String, Date], required: true },
  pdfFile: { type: [Object, null], required: false },
  instrumentId: {
    type: [String, Number],
    default: null,
  },
  link: { type: String, required: false, default: '' },
  // New preferred keys for contact info
  submitter_email: { type: String, required: false, default: undefined },
  submitter_comments: { type: String, required: false, default: undefined },
})
const emit = defineEmits([
  'update:modelValue',
  'update:email',
  'update:comments',
  'update:submitter_email',
  'update:submitter_comments',
  'update:token',
  'update:saveModalErrors',
  'update:link',
  'save',
])

const modelValueProxy = ref(props.modelValue)
// Prefer new keys if provided, fallback to legacy
const emailProxy = ref(props.submitter_email ?? props.email)
const commentsProxy = ref(props.submitter_comments ?? props.comments)
const tokenProxy = ref(props.token)
const saveModalErrorsProxy = ref({ ...props.saveModalErrors })
const linkProxy = ref(props.link)
const router = useRouter()

watch(
  () => props.modelValue,
  (val) => {
    modelValueProxy.value = val
  }
)
watch(modelValueProxy, (val) => {
  emit('update:modelValue', val)
})

watch(
  () => [props.submitter_email, props.email],
  ([newEmail, legacyEmail]) => {
    emailProxy.value = newEmail ?? legacyEmail
  }
)
watch(emailProxy, (val) => {
  emit('update:submitter_email', val)
  emit('update:email', val)
})

watch(
  () => [props.submitter_comments, props.comments],
  ([newVal, legacyVal]) => {
    commentsProxy.value = newVal ?? legacyVal
  }
)
watch(commentsProxy, (val) => {
  emit('update:submitter_comments', val)
  emit('update:comments', val)
})

watch(
  () => props.token,
  (val) => {
    tokenProxy.value = val
  }
)
watch(tokenProxy, (val) => {
  emit('update:token', val)
})

watch(
  () => props.saveModalErrors,
  (val) => {
    saveModalErrorsProxy.value = { ...val }
  }
)
watch(saveModalErrorsProxy, (val) => {
  emit('update:saveModalErrors', val)
})

watch(
  () => props.link,
  (val) => {
    linkProxy.value = val
  }
)
watch(linkProxy, (val) => {
  emit('update:link', val)
})

// Validation schema for SaveModal
const saveModalSchema = z.object({
  submitter_email: z
    .string()
    .min(1, { message: 'Email is required' })
    .email({ message: 'Please enter a valid email address' }),
  submitter_comments: z.string().optional(),
})

function validateSaveModal() {
  try {
    const modalData = {
      submitter_email: emailProxy.value,
      submitter_comments: commentsProxy.value,
    }
    saveModalSchema.parse(modalData)
    saveModalErrorsProxy.value = {}
    return true
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = {}
      error.errors.forEach((err) => {
        errors[err.path[0]] = err.message
      })
      saveModalErrorsProxy.value = errors
    }
    return false
  }
}

function onSave() {
  // Delegate submission to parent (new.vue). Validation was already performed here.
  emit('save')
}

watch(
  () => props.modelValue,
  (val) => {
    modelValueProxy.value = val
  }
)
watch(modelValueProxy, (val) => {
  emit('update:modelValue', val)
})

watch(
  () => [props.submitter_email, props.email],
  ([newEmail, legacyEmail]) => {
    emailProxy.value = newEmail ?? legacyEmail
  }
)
watch(emailProxy, (val) => {
  emit('update:submitter_email', val)
  emit('update:email', val)
})

watch(
  () => [props.submitter_comments, props.comments],
  ([newVal, legacyVal]) => {
    commentsProxy.value = newVal ?? legacyVal
  }
)
watch(commentsProxy, (val) => {
  emit('update:submitter_comments', val)
  emit('update:comments', val)
})

watch(
  () => props.token,
  (val) => {
    tokenProxy.value = val
  }
)
watch(tokenProxy, (val) => {
  emit('update:token', val)
})

function closeModal() {
  modelValueProxy.value = false
}
function handleSubmit() {
  if (validateSaveModal()) {
    onSave()
    closeModal()
  }
}
</script>
