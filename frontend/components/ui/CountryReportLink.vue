<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <UCard class="cold-ucard">
          <div class="popular-searches-container flex flex-col gap-8">
            <!-- Title Section -->
            <div>
              <h3 class="text-left md:whitespace-nowrap">
                <NuxtLink
                  v-if="processedAnswerData?.['Jurisdictions Alpha-3 code']"
                  :to="`/jurisdiction/${processedAnswerData['Jurisdictions Alpha-3 code'].toLowerCase()}`"
                >
                  Go to the country report for
                  {{
                    processedAnswerData?.Jurisdictions || 'this jurisdiction'
                  }}
                </NuxtLink>
                <span v-else>
                  Go to the country report for
                  {{
                    processedAnswerData?.Jurisdictions || 'this jurisdiction'
                  }}
                </span>
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
  processedAnswerData: {
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
