<template>
  <img
    :src="src"
    :alt="alt"
    :style="
      width
        ? { width: `${width}px`, maxWidth: '100%', height: 'auto' }
        : { maxWidth: '100%', height: 'auto' }
    "
    class="my-4 rounded-md"
  />
</template>

<script setup lang="ts">
defineProps<{
  src: string;
  alt: string;
  width?: string | number;
  height?: string | number;
}>();
</script>
