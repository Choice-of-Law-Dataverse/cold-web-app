<template>
  <UCard>
    <p>Popular Searches</p>
    <div v-for="(suggestion, index) in searchSuggestions" :key="index">
      <NuxtLink
        :to="`/search?q=${formatQuery(suggestion)}`"
        class="suggestion-link"
      >
        {{ suggestion }}
      </NuxtLink>
    </div>
  </UCard>
</template>

<script>
export default {
  data() {
    return {
      searchSuggestions: [
        'Tacit Choice in Argentina',
        'Party Autonomy in Switzerland',
      ],
    }
  },
  methods: {
    formatQuery(query) {
      return query.replace(/ /g, '+') // Replaces spaces with '+'
    },
  },
}
</script>
