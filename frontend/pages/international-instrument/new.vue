<template>
  <BaseDetailLayout
    :loading="false"
    :resultData="{}"
    :keyLabelPairs="[]"
    :valueClassMap="{}"
    sourceTable="International Instrument"
    :hideBackButton="true"
    headerMode="new"
    :showSaveModal="showSaveModal"
    @open-save-modal="openSaveModal"
    @close-save-modal="showSaveModal = false"
    :showNotificationBanner="true"
    notificationBannerMessage="You are creating a new International Instrument. Please fill in the details below. If you have questions, <a href='/contact' class='contact-link'>contact us</a>."
  >
    <!-- Always render this section, even if keyLabelPairs is empty -->
    <div class="section-gap p-0 m-0">
      <p class="label mb-2">Name</p>
      <UInput v-model="name" placeholder="Enter name..." />
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
</template>

<script setup>
import { ref } from 'vue'
import { useHead, useRouter } from '#imports'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import NotificationBanner from '~/components/ui/NotificationBanner.vue'
const name = ref('')
const router = useRouter()
const emit = defineEmits(['close-cancel-modal', 'close-save-modal'])
const showSaveModal = ref(false)

useHead({ title: 'New International Instrument — CoLD' })

function openSaveModal() {
  showSaveModal.value = true
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
