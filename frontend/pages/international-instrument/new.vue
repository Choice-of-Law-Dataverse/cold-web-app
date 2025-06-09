<template>
  <BaseDetailLayout
    :loading="false"
    :resultData="{}"
    :keyLabelPairs="[]"
    :valueClassMap="{}"
    sourceTable="International Instrument"
    :hideBackButton="true"
    headerMode="new"
    @open-save-modal="openSaveModal"
    :showNotificationBanner="true"
    :notificationBannerMessage="notificationBannerMessage"
    :icon="'i-material-symbols:warning-outline'"
  >
    <!-- Always render this section, even if keyLabelPairs is empty -->
    <div class="section-gap p-0 m-0">
      <UFormGroup size="lg" hint="Required" :error="errors.name">
        <template #label>
          <span class="label">Name</span>
        </template>
        <UInput
          v-model="name"
          class="mt-2"
          placeholder="Name of the International Instrument"
          :color="errors.name ? 'red' : 'primary'"
        />
      </UFormGroup>
    </div>
    <template #cancel-modal="{ close }">
      <div class="p-6 text-center">
        <h2 class="text-lg font-bold mb-4">Discard changes?</h2>
        <p class="mb-6">
          Are you sure you want to cancel? All unsaved changes will be lost.
        </p>
        <div class="flex justify-center gap-4">
          <UButton color="gray" variant="outline" @click="close"
            >Go Back</UButton
          >
          <UButton color="red" @click="confirmCancel">Discard</UButton>
        </div>
      </div>
    </template>
    <template #save-modal="{ close }">
      <div class="p-6 text-center">
        <h2 class="text-lg font-bold mb-4">Ready to submit?</h2>
        <p class="mb-6">
          This is a placeholder for the save/submit modal. Click Submit to send
          your data.
        </p>
        <div class="flex justify-center gap-4">
          <UButton
            color="primary"
            @click="
              () => {
                onSave()
                close()
              }
            "
            >Submit</UButton
          >
          <UButton color="gray" variant="outline" @click="close"
            >Cancel</UButton
          >
        </div>
      </div>
    </template>
  </BaseDetailLayout>

  <!-- Save Modal -->
  <UModal v-model="showSaveModal" prevent-close>
    <div class="p-6 text-center">
      <h2 class="text-lg font-bold mb-4">Ready to submit?</h2>
      <p class="mb-6">
        This is a placeholder for the save/submit modal. Click Submit to send
        your data.
      </p>
      <div class="flex justify-center gap-4">
        <UButton
          color="primary"
          @click="
            () => {
              onSave()
              showSaveModal = false
            }
          "
          >Submit</UButton
        >
        <UButton color="gray" variant="outline" @click="showSaveModal = false"
          >Cancel</UButton
        >
      </div>
    </div>
  </UModal>
</template>

<script setup>
import { ref } from 'vue'
import { useHead, useRouter } from '#imports'
import { z } from 'zod'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'

// Form data
const name = ref('')

// Validation schema
const formSchema = z.object({
  name: z
    .string()
    .min(1, { message: 'Name is required' })
    .min(3, { message: 'Name must be at least 3 characters long' }),
})

// Form validation state
const errors = ref({})

const router = useRouter()
const emit = defineEmits(['close-cancel-modal', 'close-save-modal'])
const showSaveModal = ref(false)
const notificationBannerMessage =
  'Please back up your data when working here. Data is only saved after you submit.'

useHead({ title: 'New International Instrument — CoLD' })

function validateForm() {
  try {
    const formData = {
      name: name.value,
    }

    formSchema.parse(formData)
    errors.value = {}
    return true
  } catch (error) {
    if (error instanceof z.ZodError) {
      errors.value = {}
      error.errors.forEach((err) => {
        errors.value[err.path[0]] = err.message
      })
    }
    return false
  }
}

function openSaveModal() {
  if (validateForm()) {
    showSaveModal.value = true
  }
}

function onSave() {
  const payload = {
    data_type: 'international instrument',
    data_content: {
      name: name.value,
    },
  }
  console.log('Submitting:', payload)
  fetch('https://example.com/api/international-instrument', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
    .then((res) => res.json())
    .then((data) => {
      console.log('API response:', data)
      router.push('/confirmation')
    })
    .catch((err) => {
      console.error('API error:', err)
      // Still redirect to confirmation, but with error message
      router.push('/confirmation')
    })
}

// function closeCancelModal() {
//   emit('close-cancel-modal')
// }

function confirmCancel() {
  router.push('/')
}
</script>

<style scoped>
/* Hide the back button and all right-side card header buttons */
:deep(.card-header__actions),
:deep(.card-header [class*='actions']) {
  display: none !important;
}
</style>
