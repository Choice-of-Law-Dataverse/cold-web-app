<template>
  <div class="text-sm text-gray-500">
    {{ displayMessage }}
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  error?: Error | { message?: string; statusMessage?: string } | null;
}>();

const displayMessage = computed(() => {
  if (!props.error) return "Failed to load";
  if (props.error instanceof Error) return props.error.message;
  if (props.error.statusMessage) return props.error.statusMessage;
  if (props.error.message) return props.error.message;
  return "Failed to load";
});
</script>
