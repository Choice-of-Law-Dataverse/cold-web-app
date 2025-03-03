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
          <section v-if="specialists.length">
            <span class="label">Specialists</span>
            <li
              v-for="specialist in specialists"
              :key="specialist.Specialist"
              class="result-value-small"
            >
              {{ specialist.Specialist }}
            </li>
          </section>
          <section v-else-if="specialists.length === 0 && !loading">
            <span class="label">Specialist</span>
            <p class="result-value-small">
              No specialists found for this jurisdiction.
            </p>
          </section>

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

            <p v-else-if="literatureTitle === null" class="result-value-small">
              No related literature available
            </p>
            <p v-else>Loading literature details...</p>
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
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute() // Access the route to get the ID param
const jurisdictionData = ref(null) // Store fetched jurisdiction data
const loading = ref(true) // Track loading state
const literatureTitle = ref<string | null>(null)
const specialists = ref([])

// Extract `c` query parameter
const compareJurisdiction = ref((route.query.c as string) || null)

const config = useRuntimeConfig()

// Fetch the jurisdiction details
async function fetchJurisdiction(iso2: string) {
  const jsonPayload = {
    table: 'Jurisdictions',
    filters: [{ column: 'Alpha-2 Code', value: iso2 }],
  }

  try {
    const response = await fetch(
      `${config.public.apiBaseUrl}/search/full_table`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonPayload),
      }
    )

    if (!response.ok) throw new Error('Failed to fetch jurisdiction')

    const data = await response.json()
    // Extract the required values
    jurisdictionData.value = {
      Name: data[0]?.Name || 'N/A',
      'Jurisdictional Differentiator':
        data[0]?.['Jurisdictional Differentiator'] || 'N/A',
    }

    // If "Literature" exists, fetch its title; otherwise, set a default value
    if (data[0]?.Literature) {
      jurisdictionData.value.Literature = data[0].Literature
      fetchLiteratureTitle(jurisdictionData.value.Literature)
    } else {
      literatureTitle.value = null // Ensure no loading message stays forever
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
    const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jsonPayload),
    })

    if (!response.ok) throw new Error('Failed to fetch literature details')

    const data = await response.json()
    literatureTitle.value = data.Title || 'Unknown Title' // Fallback title
  } catch (error) {
    console.error('Error fetching literature title:', error)
    literatureTitle.value = 'Error'
  }
}

// Function to fetch specialists
const fetchSpecialists = async (jurisdictionName) => {
  if (!jurisdictionName) return

  try {
    const response = await fetch(
      `${config.public.apiBaseUrl}/search/full_table`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          table: 'Specialists',
          filters: [{ column: 'Jurisdiction', value: jurisdictionName }],
        }),
      }
    )

    if (!response.ok) throw new Error('Failed to fetch specialists')

    specialists.value = await response.json()
  } catch (error) {
    console.error('Error fetching specialists:', error)
    specialists.value = []
  }
}

async function fetchInternationalInstrument(name: string) {
  const jsonPayload = {
    table: 'International Instruments',
    filters: [
      {
        column: 'Name',
        value: name,
      },
    ],
  }

  try {
    const response = await fetch(
      `${config.public.apiBaseUrl}/search/full_table`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonPayload),
      }
    )

    if (!response.ok)
      throw new Error('Failed to fetch international instrument')

    const data = await response.json()
    if (data && data.length > 0) {
      // Use the returned "Name" as the jurisdiction's name
      jurisdictionData.value = {
        Name: data[0]?.Name || 'N/A',
      }
      // If there's a Literature field, fetch its title as before
      if (data[0]?.Literature) {
        jurisdictionData.value.Literature = data[0].Literature
        fetchLiteratureTitle(jurisdictionData.value.Literature)
      } else {
        literatureTitle.value = null
      }
    } else {
      jurisdictionData.value = null // or set an error message
    }
  } catch (error) {
    console.error('Error fetching international instrument:', error)
  }
}

async function fetchJurisdictionData(identifier: string) {
  // Attempt to fetch as a domestic jurisdiction first
  await fetchJurisdiction(identifier)

  // If no valid data is returned (for example, Name is missing or 'N/A'),
  // then try fetching from International Instruments
  if (!jurisdictionData.value || jurisdictionData.value.Name === 'N/A') {
    console.log(
      'Domestic jurisdiction not found, trying international instruments...'
    )
    await fetchInternationalInstrument(identifier)
  }
}

// Fetch specialists when jurisdictionData.Name changes
watch(
  () => jurisdictionData.value?.Name,
  (newName) => {
    if (newName) fetchSpecialists(newName)
  }
)

const keyLabelPairs = computed(() => {
  const pairs = [
    { key: 'Name', label: 'Jurisdiction' },
    {
      key: 'Jurisdictional Differentiator',
      label: 'Jurisdictional Differentiator',
    },
    { key: 'Specialist', label: 'Specialist' },
    { key: 'Literature', label: 'Related Literature' },
  ]
  return pairs
})

const valueClassMap = {
  Name: 'result-value-medium',
  'Jurisdictional Differentiator': 'result-value-small',
}

// Fetch jurisdiction data on component mount
onMounted(() => {
  const identifier = (route.params.id as string).replace(/_/g, ' ') // Convert '_' to spaces
  fetchJurisdictionData(identifier)

  const jurisdictionName = (route.params.id as string).replace(/_/g, ' ') // Convert '_' to spaces
  fetchJurisdiction(jurisdictionName)
  if (jurisdictionData.value?.Name)
    fetchSpecialists(jurisdictionData.value.Name)
})

// Watch for changes to the `c` query parameter and update `compareJurisdiction`
watch(
  () => route.query.c,
  (newCompare) => {
    compareJurisdiction.value = (newCompare as string) || null
  }
)
</script>
