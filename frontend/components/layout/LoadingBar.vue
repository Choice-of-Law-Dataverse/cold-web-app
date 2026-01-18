<template>
  <div class="mb-2.5 space-y-2">
    <USkeleton
      class="h-2 rounded-none"
      :style="{
        backgroundColor: 'var(--color-cold-gray-alpha)',
        width: randomWidth,
      }"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";

const randomWidth = ref("280px");

onMounted(() => {
  randomWidth.value = `${Math.floor(Math.random() * (350 - 200 + 1)) + 200}px`;
});
</script>
