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
        :error="saveModalErrorsProxy.email"
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
import { ref, watch, toRefs } from 'vue'
import { z } from 'zod'
import { useRouter } from '#imports'
import { format } from 'date-fns'

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
})
const emit = defineEmits([
  'update:modelValue',
  'update:email',
  'update:comments',
  'update:token',
  'update:saveModalErrors',
  'save',
])

const modelValueProxy = ref(props.modelValue)
const emailProxy = ref(props.email)
const commentsProxy = ref(props.comments)
const tokenProxy = ref(props.token)
const saveModalErrorsProxy = ref({ ...props.saveModalErrors })
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
  () => props.email,
  (val) => {
    emailProxy.value = val
  }
)
watch(emailProxy, (val) => {
  emit('update:email', val)
})

watch(
  () => props.comments,
  (val) => {
    commentsProxy.value = val
  }
)
watch(commentsProxy, (val) => {
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

// Validation schema for SaveModal
const saveModalSchema = z.object({
  email: z
    .string()
    .min(1, { message: 'Email is required' })
    .email({ message: 'Please enter a valid email address' }),
  comments: z.string().optional(),
})

function validateSaveModal() {
  try {
    const modalData = {
      email: emailProxy.value,
      comments: commentsProxy.value,
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
  const mergedSpecialists = (props.specialists || [])
    .filter((s) => s && s.trim())
    .join(', ')
  const payload = {
    data_type: 'international instrument',
    data_content: {
      name: props.name,
      specialists: mergedSpecialists,
      date: format(new Date(props.date), 'yyyy-MM-dd'),
      pdf: props.pdfFile && props.pdfFile.name ? props.pdfFile.name : null,
    },
    user: {
      email: emailProxy.value,
      comments: commentsProxy.value || null,
    },
  }
  if (!payload.data_content.pdf) {
    delete payload.data_content.pdf
  }
  if (!payload.user.comments) {
    delete payload.user.comments
  }
  console.log('Submitting: ' + JSON.stringify(payload, null, 2))
  emit('save', payload)
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
  () => props.email,
  (val) => {
    emailProxy.value = val
  }
)
watch(emailProxy, (val) => {
  emit('update:email', val)
})

watch(
  () => props.comments,
  (val) => {
    commentsProxy.value = val
  }
)
watch(commentsProxy, (val) => {
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
