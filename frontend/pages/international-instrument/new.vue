<template>
  <BaseDetailLayout
    :loading="false"
    :resultData="{}"
    :keyLabelPairs="[]"
    :valueClassMap="{}"
    sourceTable="International Instrument"
    :hideBackButton="true"
    headerMode="new"
    @save="onSave"
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
  </BaseDetailLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useHead, useRouter } from '#imports'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
const name = ref('')
const router = useRouter()
const emit = defineEmits(['close-cancel-modal'])

useHead({ title: 'New International Instrument — CoLD' })

function onSave() {
  const payload = {
    data_type: 'international instrument',
    data_content: {
      name: name.value,
    },
  }
  console.log('Submitting:', payload)
  // Placeholder API call
  fetch('https://example.com/api/international-instrument', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
    .then((res) => res.json())
    .then((data) => console.log('API response:', data))
    .catch((err) => console.error('API error:', err))
}

function closeCancelModal() {
  emit('close-cancel-modal')
}

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
