<template>
  <USelectMenu
    searchable
    searchable-placeholder="Search a Jurisdiction..."
    class="w-72 lg:w-96 cold-uselectmenu"
    placeholder="Pick a Jurisdiction"
    :options="countries"
    v-model="selected"
    @change="onSelect"
    size="xl"
  />
</template>

<script setup>
// Props for the country options
defineProps({
  countries: {
    type: Array,
    required: true,
  },
})

// Emit selection back to the parent
const emit = defineEmits(['countrySelected'])

const selected = defineModel() // v-model integration

const onSelect = (value) => {
  emit('countrySelected', value) // Emit the selected value
}
</script>
