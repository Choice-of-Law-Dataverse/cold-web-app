<template>
  <div class="flex space-x-4">
    <div
      v-for="(count, status) in counts"
      :key="status"
      class="flex items-center space-x-2"
    >
      <!-- Tooltip Wrapper -->
      <UTooltip
        :text="getTooltipText(status, count)"
        :popper="{ arrow: true, placement: 'top' }"
        :ui="{
          background: 'bg-cold-night',
          color: 'text-white',
          base: 'pt-3 pr-3 pb-7 pl-3',
          rounded: 'rounded-none',
          ring: '',
          arrow: {
            base: 'before:visible before:block before:rotate-45 before:z-[-1] before:w-2 before:h-2',
            background: 'before:bg-cold-night',
            ring: '',
          },
        }"
      >
        <div class="flex items-center space-x-2">
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
              class="inline-block h-4 w-4 rounded-full"
            />
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
      </UTooltip>
    </div>
  </div>
</template>

<script setup>
defineProps({
  counts: {
    type: Object,
    required: true,
  },
});

// Function to return tooltip text based on status and count
function getTooltipText(status, count) {
  switch (status) {
    case "green":
      return `Positive Match`;
    case "red":
      return `Negative Match`;
    case "red-x":
      return `Mismatch`;
    default:
      return `Not Applicable`;
  }
}
</script>

<style scoped>
.bg-cold-night {
  background-color: var(--color-cold-night);
}

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
