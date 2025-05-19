<template>
  <UCard class="cold-ucard">
    <h2 class="popular-title">{{ title }}</h2>
    <div class="number-container">
      <span v-if="!loading && !error">{{ number }}</span>
      <span v-else-if="loading"><LoadingNumber /></span>
      <span v-else>Error</span>
    </div>
    <div class="link-container">
      <a :href="buttonLink">
        <UButton
          class="suggestion-button"
          variant="link"
          icon="i-material-symbols:arrow-forward"
          trailing
        >
          {{ buttonText }}
        </UButton>
      </a>
    </div>
  </UCard>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import LoadingNumber from '../layout/LoadingNumber.vue'
const props = defineProps({
  title: { type: String, required: true },
  buttonText: { type: String, required: true },
  buttonLink: { type: String, required: true },
  tableName: { type: String, required: true },
})

const number = ref(null)
const loading = ref(true)
const error = ref(false)

const config = useRuntimeConfig()

async function fetchNumber() {
  loading.value = true
  error.value = false
  try {
    const body = {
      search_string: '',
      filters: [
        {
          column: 'tables',
          values: [props.tableName],
        },
      ],
    }
    const response = await fetch(`${config.public.apiBaseUrl}/search/`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    if (!response.ok) throw new Error('API error')
    const data = await response.json()
    number.value = data.total_matches ?? 0
  } catch (e) {
    error.value = true
    number.value = 0
  } finally {
    loading.value = false
  }
}

onMounted(fetchNumber)
watch(() => props.tableName, fetchNumber)
</script>

<style scoped>
h2 {
  text-align: center;
}
.number-container {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 90px;
  font-weight: 700;
}
.link-container {
  display: flex;
  justify-content: center;
}
</style>
