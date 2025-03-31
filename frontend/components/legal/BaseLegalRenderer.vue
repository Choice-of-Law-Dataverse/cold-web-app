<template>
  <div>
    <div v-if="hasContent">
      <ul v-if="isList">
        <li
          v-for="(item, index) in items"
          :key="index"
          :class="valueClassMap || defaultClass"
        >
          <slot :item="item" />
        </li>
      </ul>
      <div v-else :class="valueClassMap || defaultClass">
        <slot :item="items[0]" />
      </div>
    </div>
    <div v-else>
      <span>N/A</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: {
    type: [Array, String],
    default: () => []
  },
  valueClassMap: {
    type: String,
    default: ''
  },
  defaultClass: {
    type: String,
    default: 'result-value'
  },
  isList: {
    type: Boolean,
    default: true
  }
})

const hasContent = computed(() => {
  if (Array.isArray(props.items)) {
    return props.items.length > 0
  }
  return props.items && props.items.trim()
})
</script> 