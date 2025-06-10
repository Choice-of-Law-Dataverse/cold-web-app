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
          <InfoTooltip :text="tooltipInternationalInstrumentName" />
        </template>
        <UInput
          v-model="name"
          class="mt-2"
          placeholder="Name of the International Instrument"
        />
      </UFormGroup>
      <UFormGroup size="lg" class="mt-8">
        <template #label>
          <span class="label">Specialists</span>
          <InfoTooltip :text="tooltipInternationalInstrumentSpecialist" />
        </template>
        <div
          v-for="(specialist, idx) in specialists"
          :key="idx"
          class="flex items-center mt-2"
        >
          <UInput
            v-model="specialists[idx]"
            placeholder="Specialist's name"
            class="flex-1"
          />
          <UButton
            v-if="idx > 0"
            icon="i-heroicons-x-mark"
            color="red"
            variant="ghost"
            class="ml-2"
            @click="removeSpecialist(idx)"
            aria-label="Remove specialist"
          />
        </div>
        <template v-for="(specialist, idx) in specialists">
          <div
            v-if="specialists[idx] && idx === specialists.length - 1"
            :key="'add-btn-' + idx"
          >
            <UButton
              class="mt-2"
              color="primary"
              variant="soft"
              icon="i-heroicons-plus"
              @click="addSpecialist"
              >Add another specialist</UButton
            >
          </div>
        </template>
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
    <!-- Removed duplicate save modal template - using standalone UModal below -->
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
import InfoTooltip from '~/components/ui/InfoTooltip.vue'
import tooltipInternationalInstrumentName from '@/content/info_boxes/international_instrument/name.md?raw'
import tooltipInternationalInstrumentSpecialist from '@/content/info_boxes/international_instrument/specialists.md?raw'

// Form data
const name = ref('')
const specialists = ref([''])

// Validation schema
const formSchema = z.object({
  name: z
    .string()
    .min(1, { message: 'Name is required' })
    .min(3, { message: 'Name must be at least 3 characters long' }),
  specialists: z.array(z.string()).optional(),
})

// Form validation state
const errors = ref({})

const router = useRouter()
const emit = defineEmits(['close-cancel-modal', 'close-save-modal'])
const showSaveModal = ref(false)
const notificationBannerMessage =
  'Please back up your data when working here. Closing or reloading this window will delete everything. Data is only saved after you submit.'

useHead({ title: 'New International Instrument — CoLD' })

function validateForm() {
  try {
    const formData = {
      name: name.value,
      specialists: specialists.value,
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
  const isValid = validateForm()

  if (isValid) {
    showSaveModal.value = true
  }
}

function onSave() {
  const mergedSpecialists = specialists.value
    .filter((s) => s && s.trim())
    .join(', ')
  const payload = {
    data_type: 'international instrument',
    data_content: {
      name: name.value,
      specialists: mergedSpecialists,
    },
  }
  // Print payload as a single, clear console log (matches alert)
  console.log('Submitting: ' + JSON.stringify(payload, null, 2))
  router.push('/confirmation')
}

function confirmCancel() {
  router.push('/')
}

function addSpecialist() {
  specialists.value.push('')
}
function removeSpecialist(idx) {
  specialists.value.splice(idx, 1)
}
</script>

<style scoped>
/* Hide the back button and all right-side card header buttons */
:deep(.card-header__actions),
:deep(.card-header [class*='actions']) {
  display: none !important;
}
</style>
