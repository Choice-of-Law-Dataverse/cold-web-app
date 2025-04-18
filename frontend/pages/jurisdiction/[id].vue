<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <DetailDisplay
          :loading="loading"
          :resultData="jurisdictionData"
          :keyLabelPairs="keyLabelPairs"
          :valueClassMap="valueClassMap"
          :formattedJurisdiction="[jurisdictionData?.Name]"
        >
          <!-- Specialists Section -->
          <section>
            <span class="label">Specialists</span>
            <template v-if="specialists.length">
              <ul>
                <li
                  v-for="specialist in specialists"
                  :key="specialist.Specialist"
                  class="result-value-small"
                >
                  {{ specialist.Specialist }}
                </li>
              </ul>
            </template>
            <p v-else class="result-value-small">
              {{
                keyLabelPairs.find((pair) => pair.key === 'Specialist')
                  ?.emptyValueBehavior?.fallback || 'No specialists available'
              }}
            </p>
          </section>

          <template #literature>
            <section>
              <span class="label">Related Literature</span>
              <RelatedLiterature
                :literature-id="jurisdictionData?.Literature"
                :literature-title="literatureTitle"
                :valueClassMap="valueClassMap['Related Literature']"
                :showLabel="false"
                :emptyValueBehavior="
                  keyLabelPairs.find((pair) => pair.key === 'Literature')
                    ?.emptyValueBehavior
                "
                use-id
              />
            </section>
          </template>

          <template #search-links>
            <span class="label !mt-[-36px] !mb-5">Related Data</span>
            <NuxtLink
              :to="{
                name: 'search',
                query: {
                  type: 'Court Decisions',
                  jurisdiction: jurisdictionData?.Name || '',
                },
              }"
              class="no-underline !mb-2"
            >
              <UButton
                class="link-button"
                variant="link"
                icon="i-material-symbols:arrow-forward"
                trailing
              >
                <span class="break-words text-left">
                  All court decisions from {{ jurisdictionData?.Name || 'N/A' }}
                </span>
              </UButton>
            </NuxtLink>

            <NuxtLink
              :to="{
                name: 'search',
                query: {
                  type: 'Legal Instruments',
                  jurisdiction: jurisdictionData?.Name || '',
                },
              }"
              class="no-underline"
            >
              <UButton
                class="link-button"
                variant="link"
                icon="i-material-symbols:arrow-forward"
                trailing
              >
                <span class="break-words text-left">
                  All legal instruments from
                  {{ jurisdictionData?.Name || 'N/A' }}
                </span>
              </UButton>
            </NuxtLink>
          </template>
        </DetailDisplay>

        <!-- Error State -->
        <div v-if="error" class="text-red-500 mt-4">
          {{ error }}
        </div>

        <!-- Only render JurisdictionComparison if jurisdictionData is loaded -->
        <JurisdictionComparison
          v-if="!loading && jurisdictionData?.Name"
          :jurisdiction="jurisdictionData.Name"
          :compareJurisdiction="compareJurisdiction"
        />
      </div>
    </div>
  </main>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DetailDisplay from '~/components/ui/BaseDetailDisplay.vue'
import JurisdictionComparison from '~/components/jurisdiction-comparison/JurisdictionComparison.vue'
import RelatedLiterature from '~/components/literature/RelatedLiterature.vue'
import { useJurisdiction } from '~/composables/useJurisdiction'

const route = useRoute()
const router = useRouter()
const {
  loading,
  error,
  jurisdictionData,
  literatureTitle,
  specialists,
  compareJurisdiction,
  keyLabelPairs,
  valueClassMap,
  fetchJurisdiction,
} = useJurisdiction()

// Set compare jurisdiction from query parameter
compareJurisdiction.value = route.query.c || null

onMounted(async () => {
  try {
    const id = route.params.id
    await fetchJurisdiction(id)
  } catch (err) {
    if (err.message === 'no entry found with the specified id') {
      router.push({
        path: '/error',
        query: { message: 'Jurisdiction not found' },
      })
    } else {
      console.error('Error fetching jurisdiction:', err)
    }
  }
})
</script>
