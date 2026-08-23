<template>
  <div />
</template>

<script setup lang="ts">
/**
 * `/learn` is a section entry point with no content of its own. The redirect
 * runs as route middleware rather than in `onMounted` so it is a real 301 for
 * crawlers instead of a blank page they would index.
 */
definePageMeta({
  middleware: [
    () =>
      navigateTo("/learn/open-educational-resources", {
        redirectCode: 301,
        replace: true,
      }),
  ],
});
</script>
