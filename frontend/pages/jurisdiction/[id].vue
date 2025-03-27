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
            <RelatedLiterature
              v-if="jurisdictionData?.Literature"
              :literature-id="jurisdictionData.Literature"
              :literature-title="literatureTitle"
              :valueClassMap="valueClassMap['Related Literature']"
              use-id
            />
            <p v-else class="result-value-small">
              No related literature available
            </p>
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
async function fetchJurisdiction(iso3: string) {
  const jsonPayload = {
    table: 'Jurisdictions',
    //filters: [{ column: 'Alpha-3 Code', value: iso3 }],
    id: iso3.toUpperCase(),
  }

  try {
    const response = await fetch(
      //`${config.public.apiBaseUrl}/search/full_table`,
      `${config.public.apiBaseUrl}/search/details`,
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
      Name: data?.Name || 'N/A',
      'Jurisdictional Differentiator':
        data?.['Jurisdictional Differentiator'] || 'N/A',
    }

    // If "Literature" exists, fetch its title; otherwise, set a default value
    if (data?.Literature) {
      jurisdictionData.value.Literature = data.Literature
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

async function fetchLiteratureTitle(ids: string) {
  if (!ids) {
    literatureTitle.value = ''
    return
  }

  // Split IDs if multiple are provided
  const idList = ids.split(',').map((id) => id.trim())

  try {
    const titles = await Promise.all(
      idList.map(async (id) => {
        const jsonPayload = {
          table: 'Literature',
          id: id,
        }
        const response = await fetch(
          `${config.public.apiBaseUrl}/search/details`,
          {
            method: 'POST',
            headers: {
              authorization: `Bearer ${config.public.FASTAPI}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonPayload),
          }
        )
        if (!response.ok) throw new Error('Failed to fetch literature details')
        const data = await response.json()
        return data.Title || 'Unknown Title'
      })
    )
    literatureTitle.value = titles
  } catch (error) {
    console.error('Error fetching literature title:', error)
    literatureTitle.value = 'Error'
  }
}

async function fetchJurisdictionData(identifier: string) {
  // Attempt to fetch as a domestic jurisdiction first
  await fetchJurisdiction(identifier)
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
    { key: 'Literature', label: '' },
  ]
  // Only include "Jurisdictional Differentiator" if it exists in jurisdictionData
  if (!jurisdictionData.value?.['Jurisdictional Differentiator']) {
    return pairs.filter((pair) => pair.key !== 'Jurisdictional Differentiator')
  }
  return pairs
})

const valueClassMap = {
  Name: 'result-value-medium',
  'Jurisdictional Differentiator': 'result-value-small',
}

// Fetch jurisdiction data on component mount
onMounted(() => {
  const identifier = (route.params.id as string)
    .toLowerCase()
    .replace(/-/g, ' ')
  fetchJurisdictionData(identifier)
})

// Watch for changes to the `c` query parameter and update `compareJurisdiction`
watch(
  () => route.query.c,
  (newCompare) => {
    compareJurisdiction.value = (newCompare as string) || null
  }
)
</script>
