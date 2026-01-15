<template>
  <div
    class="detail-row hover-row flex flex-col gap-3 md:flex-row md:items-start md:gap-10"
  >
    <div class="label-key md:w-44 md:flex-shrink-0">
      <span class="flex items-center gap-1.5">
        {{ label }}
        <slot name="label-actions" />
        <InfoPopover v-if="tooltip" :text="tooltip" />
      </span>
    </div>

    <div class="detail-value md:flex-1">
      <slot />
    </div>
  </div>
</template>

<script setup>
import InfoPopover from "@/components/ui/InfoPopover.vue";

defineProps({
  label: {
    type: String,
    required: true,
  },
  tooltip: {
    type: String,
    default: undefined,
  },
});
</script>

<style scoped>
.detail-row {
  padding-top: 1rem;
  padding-bottom: 1rem;
  margin: 0 -1.5rem;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}

.label-key {
  padding: 0;
}

.label-key span {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
}

/* InfoPopover icon styling */
.label-key :deep(svg) {
  color: rgb(156 163 175); /* gray-400 */
  transition: color 0.2s ease;
}

.label-key:hover :deep(svg) {
  color: rgb(107 114 128); /* gray-500 - subtle change */
}
</style>
