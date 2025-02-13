<template>
  <ul>
    <li v-for="(source, index) in sources" :key="index" :class="valueClass">
      <LegalProvisionRenderer
        :value="source"
        :fallbackData="fallbackData"
        :valueClassMap="valueClassMap"
      />
    </li>
  </ul>
</template>

<script setup>
defineProps({
  sources: Array,
  fallbackData: Object,
  valueClassMap: Object,
  valueClass: {
    type: String,
    default: 'result-value-medium',
  },
})
</script>
