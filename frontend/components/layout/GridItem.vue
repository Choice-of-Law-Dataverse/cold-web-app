<template>
  <div :class="columnClasses">
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  cols: {
    type: [Number, String],
    default: 12,
    validator: (value) => {
      const num = Number(value)
      return num >= 1 && num <= 12
    },
  },
  mdCols: {
    type: [Number, String],
    default: null,
    validator: (value) => {
      if (value === null) return true
      const num = Number(value)
      return num >= 1 && num <= 12
    },
  },
  lgCols: {
    type: [Number, String],
    default: null,
    validator: (value) => {
      if (value === null) return true
      const num = Number(value)
      return num >= 1 && num <= 12
    },
  },
})

const columnClasses = computed(() => {
  const classes = [`col-span-${props.cols}`]

  if (props.mdCols) {
    classes.push(`md:col-span-${props.mdCols}`)
  }

  if (props.lgCols) {
    classes.push(`lg:col-span-${props.lgCols}`)
  }

  return classes.join(' ')
})
</script>
