<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <DetailDisplay
          :loading="loading"
          :resultData="jurisdictionData"
          :keyLabelPairs="keyLabelPairs"
          :valueClassMap="valueClassMap"
        >
          <template #literature>
            <NuxtLink
              v-if="literatureTitle && jurisdictionData?.Literature"
              :to="`/literature/${jurisdictionData.Literature}`"
              class="no-underline pb-4 block pt-2"
            >
              <UButton class="link-button" variant="link">
                <span class="break-words text-left">
                  {{ literatureTitle }}
                </span>
              </UButton>
            </NuxtLink>

            <p v-else class="text-gray-500">Loading literature details...</p>
          </template>

          <template #search-links>
            <span class="label">related data</span>
            <NuxtLink
              :to="{
                name: 'search',
                query: {
                  type: 'Court Decisions',
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

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
//import DetailDisplay from '~/components/DetailDisplay.vue'
//import JurisdictionComparison from '~/components/JurisdictionComparison.vue'
//import JurisdictionComparisonInfo from '~/components/JurisdictionComparisonInfo.vue'

const route = useRoute() // Access the route to get the ID param
//const router = useRouter()
const jurisdictionData = ref(null) // Store fetched jurisdiction data
const loading = ref(true) // Track loading state
const literatureTitle = ref<string | null>(null)

// Extract `c` query parameter
const compareJurisdiction = ref((route.query.c as string) || null)

const config = useRuntimeConfig()

// Fetch the jurisdiction details
async function fetchJurisdiction(iso2: string) {
  const jsonPayload = {
    table: 'Jurisdictions',
    filters: [{ column: 'Alpha-2 code', value: iso2 }],
  }

  try {
    const response = await fetch(`${config.public.apiBaseUrl}/full_table`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(jsonPayload),
    })

    if (!response.ok) throw new Error('Failed to fetch jurisdiction')

    const data = await response.json()
    // Extract the required values
    jurisdictionData.value = {
      Name: data[0]?.Name || 'N/A',
      'Jurisdictional differentiator':
        data[0]?.['Jurisdictional differentiator'] || 'N/A',
      Literature: data[0]?.Literature || '',
    }

    // Fetch literature title if a Literature ID exists
    if (jurisdictionData.value.Literature) {
      fetchLiteratureTitle(jurisdictionData.value.Literature)
    }
  } catch (error) {
    console.error('Error fetching jurisdiction:', error)
  } finally {
    loading.value = false
  }
}

async function fetchLiteratureTitle(id: string) {
  const jsonPayload = {
    table: 'Literature',
    id: id,
  }

  try {
    const response = await fetch(
      `${config.public.apiBaseUrl}/curated_search/details`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsonPayload),
      }
    )

    if (!response.ok) throw new Error('Failed to fetch literature details')

    const data = await response.json()
    literatureTitle.value = data.Title || 'Unknown Title' // Fallback title
  } catch (error) {
    console.error('Error fetching literature title:', error)
    literatureTitle.value = 'Error'
  }
}

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  { key: 'Name', label: 'Jurisdiction' },
  {
    key: 'Jurisdictional differentiator',
    label: 'Jurisdictional differentiator',
  },
  { key: 'Literature', label: 'Related Literature' }, // Add this
]

const valueClassMap = {
  Name: 'result-value-medium',
  'Jurisdictional differentiator': 'result-value-small',
}

// Fetch jurisdiction data on component mount
onMounted(() => {
  const jurisdictionName = (route.params.id as string).replace(/_/g, ' ') // Convert '_' to spaces
  fetchJurisdiction(jurisdictionName)
})

// Watch for changes to the `c` query parameter and update `compareJurisdiction`
watch(
  () => route.query.c,
  (newCompare) => {
    compareJurisdiction.value = (newCompare as string) || null
  }
)
</script>
