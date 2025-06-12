<template>
  <div v-if="isEditPage">
    <h1>Edit International Instrument</h1>
    <!-- Your edit content here -->
  </div>
  <div v-else>
    <!-- Handle other cases or redirect -->
    Page not found
  </div>
</template>

<script setup>
const route = useRoute()

// Check if this is an edit page (slug ends with 'edit')
const isEditPage = computed(() => {
  const slug = route.params.slug
  return Array.isArray(slug) && slug.length === 2 && slug[1] === 'edit'
})

// Get the ID from the slug
const instrumentId = computed(() => {
  const slug = route.params.slug
  return Array.isArray(slug) ? slug[0] : null
})
</script>
