<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <UCard class="cold-ucard">
          <div class="popular-searches-container flex flex-col gap-8">
            <!-- Title Section -->
            <div>
              <h3 class="text-left md:whitespace-nowrap">
                Compare
                {{ formattedJurisdiction?.Name || 'this jurisdiction' }} with
                other jurisdictions
              </h3>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </main>
</template>

<script setup>
// Accept processedAnswerData as a prop from parent
defineProps({
  formattedJurisdiction: {
    type: Object,
    required: true,
  },
})
</script>

<style scoped>
h3 {
  color: var(--color-cold-purple) !important;
}
</style>
