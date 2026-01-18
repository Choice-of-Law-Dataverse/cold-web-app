<template>
  <div
    v-if="date"
    class="font-italics flex justify-end px-6 pb-4 text-xs text-gray-500"
  >
    <span class="flex items-center gap-1">
      Last updated {{ date }}

      <UIcon name="i-heroicons-clock" class="size-4" />
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  date?: string;
}>();
</script>
