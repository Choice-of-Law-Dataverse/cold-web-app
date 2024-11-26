<template>
  <div class="flex justify-end space-x-4">
    <div
      v-for="(count, status) in counts"
      :key="status"
      class="flex items-center space-x-2"
    >
      <span
        :style="{
          backgroundColor:
            status === 'green'
              ? 'var(--color-cold-green)'
              : status === 'red'
                ? 'var(--color-cold-red)'
                : status === 'red-x'
                  ? 'var(--color-cold-red)'
                  : 'var(--color-cold-gray)',
        }"
        class="inline-block w-4 h-4 rounded-full"
      ></span>
      <span class="text-sm">{{ count }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  counts: {
    type: Object,
    required: true,
  },
})
</script>

<style scoped>
/* Optional: Style adjustments for alignment */
</style>
