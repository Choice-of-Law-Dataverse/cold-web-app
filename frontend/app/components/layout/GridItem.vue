<template>
  <div :class="columnClasses">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface Props {
  cols?: number | string;
  mdCols?: number | string | null;
  lgCols?: number | string | null;
}

const props = withDefaults(defineProps<Props>(), {
  cols: 12,
  mdCols: null,
  lgCols: null,
});

const columnClasses = computed(() => {
  const classes = [`col-span-${props.cols}`];

  if (props.mdCols) {
    classes.push(`md:col-span-${props.mdCols}`);
  }

  if (props.lgCols) {
    classes.push(`lg:col-span-${props.lgCols}`);
  }

  return classes.join(" ");
});
</script>
