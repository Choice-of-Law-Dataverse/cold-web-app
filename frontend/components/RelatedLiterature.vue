<template>
  <div>
    <span class="label">Related Literature</span>

    <!-- If we're using literature ID mode -->
    <template v-if="useId">
      <ul>
        <li v-for="(id, index) in literatureIds" :key="id">
          <NuxtLink
            :to="`/literature/${literatureId}`"
            class="no-underline pb-4 block pt-2"
          >
            <UButton class="link-button" variant="link">
              <span class="break-words text-left">
                {{ literatureTitle }}
              </span>
            </UButton>
          </NuxtLink>
        </li>
      </ul>
    </template>

    <!-- Else, use the normal themes-based display -->
    <template v-else>
      <ul v-if="loading">
        <li class="text-gray-500">Loading...</li>
      </ul>

      <ul v-else-if="literatureList.length">
        <li
          v-for="(item, index) in displayedLiterature"
          :key="index"
          :class="valueClassMap"
        >
          <NuxtLink :to="`/literature/${item.id}`">
            {{ item.title }}
          </NuxtLink>
        </li>

        <!-- Show more link replaces the fourth bullet point -->
        <li
          v-if="literatureList.length > 5 && !showAll"
          class="list-none mt-[-2px]"
        >
          <NuxtLink
            @click.prevent="showAll = true"
            class="link-button cursor-pointer"
          >
            <Icon
              name="material-symbols:add"
              class="text-base translate-y-[3px]"
            />
            Show more related literature
          </NuxtLink>
        </li>

        <!-- Show less button when expanded -->
        <NuxtLink
          v-if="literatureList.length > 5 && showAll"
          class="link-button list-none mt-[-2px] cursor-pointer"
          @click="showAll = false"
        >
          <Icon
            name="material-symbols:remove"
            class="text-base translate-y-[3px]"
          />
          Show less related literature
        </NuxtLink>
      </ul>

      <p v-if="!literatureList.length && !loading" :class="valueClassMap">
        No related literature available
      </p>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watchEffect } from 'vue'

const config = useRuntimeConfig()

// Props: themes for search
const props = defineProps({
  themes: {
    type: String,
    required: true,
  },
  valueClassMap: {
    type: String,
    default: 'result-value-small',
  },
  literatureId: { type: String, default: '' },
  literatureTitle: { type: String, default: '' },
  useId: { type: Boolean, default: false },
})

// Split the literatureId string into an array
const literatureIds = computed(() => {
  return props.literatureId
    ? props.literatureId.split(',').map((item) => item.trim())
    : []
})

// Similarly, if the API returns multiple literature titles, split them too.
const literatureTitles = computed(() => {
  return props.literatureTitle
    ? props.literatureTitle.split(',').map((item) => item.trim())
    : []
})

// Reactive variables
const literatureList = ref<{ id: string; title: string }[]>([])
const totalMatches = ref(0)
const loading = ref(true)
const showAll = ref(false)

// Computed property: Show nothing initially if the list is longer than 5
const displayedLiterature = computed(() => {
  if (!showAll.value) {
    return literatureList.value.length > 5
      ? literatureList.value.slice(0, 3)
      : literatureList.value
  }
  return literatureList.value
})

// Function to fetch related literature
async function fetchRelatedLiterature(themes: string) {
  if (!themes) return

  const jsonPayload = {
    filters: [
      { column: 'tables', values: ['Literature'] },
      { column: 'themes', values: themes.split(',').map((t) => t.trim()) },
    ],
  }

  try {
    const response = await fetch(`${config.public.apiBaseUrl}/search/`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jsonPayload),
    })

    if (!response.ok) throw new Error('Failed to fetch related literature')

    const data = await response.json()
    literatureList.value = Object.values(data.results).map((item: any) => ({
      title: item.Title,
      id: item.id,
    }))
    totalMatches.value = data.total_matches // Store total matches count
  } catch (error) {
    console.error('Error fetching related literature:', error)
  } finally {
    loading.value = false
  }
}

// Fetch data when themes change
watchEffect(() => {
  fetchRelatedLiterature(props.themes)
})
</script>
