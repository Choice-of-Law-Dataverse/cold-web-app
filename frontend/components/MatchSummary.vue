<template>
  <div class="flex space-x-4">
    <div
      v-for="(count, status) in counts"
      :key="status"
      class="flex items-center space-x-2"
    >
      <!-- Status Indicator -->
      <template v-if="status !== 'red-x'">
        <span
          :style="{
            backgroundColor:
              status === 'green'
                ? 'var(--color-cold-green)'
                : status === 'red'
                  ? 'var(--color-label-court-decision)'
                  : 'var(--color-cold-gray)',
          }"
          class="inline-block w-4 h-4 rounded-full"
        ></span>
      </template>
      <template v-else>
        <span
          :style="{ color: 'var(--color-label-court-decision)' }"
          class="text-lg"
        >
          ✖
        </span>
      </template>

      <!-- Count with Matching Color -->
      <span
        :style="{
          color:
            status === 'green'
              ? 'var(--color-cold-green)'
              : status === 'red'
                ? 'var(--color-label-court-decision)'
                : status === 'red-x'
                  ? 'var(--color-label-court-decision)'
                  : 'var(--color-cold-gray)',
        }"
        class="label"
      >
        {{ count }}
      </span>
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
.rounded-full {
  border-radius: 50%;
}

.inline-block {
  display: inline-block;
}

.w-4 {
  width: 12px;
}

.h-4 {
  height: 12px;
}
</style>
