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
    <template #cancel-modal>
      <div class="p-6 text-center">
        <h2 class="text-lg font-bold mb-4">Discard changes?</h2>
        <p class="mb-6">
          Are you sure you want to cancel? All unsaved changes will be lost.
        </p>
        <div class="flex justify-center gap-4">
          <UButton color="gray" variant="outline" @click="closeCancelModal"
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
  // Find the BaseCardHeader instance and set isOpen to false
  // This works because the slot is rendered in the context of BaseCardHeader
  // so $parent is the header component
  // But in Vue 3, you can't access $parent directly from the slot, so instead,
  // emit an event or use a shared state/store if you want to control it from here.
  // For now, the modal can be closed from inside BaseCardHeader only.
  // This button is for demonstration.
  // You may want to expose a prop or event for more advanced control.
  // Or, you can use a custom event on the modal slot and listen in BaseCardHeader.
}

function confirmCancel() {
  // Example: navigate away
  router.push('/international-instrument')
}
</script>

<style scoped>
/* Hide the back button and all right-side card header buttons */
:deep(.card-header__actions),
:deep(.card-header [class*='actions']) {
  display: none !important;
}
</style>
