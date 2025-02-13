<template>
  <ul>
    <li v-for="(source, index) in sources" :key="index" :class="valueClass">
      <template v-if="noLinkList.includes(source)">
        <span>{{ source }}</span>
      </template>
      <template v-else>
        <LegalProvisionRenderer
          :value="source"
          :fallbackData="fallbackData"
          :valueClassMap="valueClassMap"
        />
      </template>
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
  noLinkList: {
    type: Array,
    default: () => [],
  },
})
</script>
