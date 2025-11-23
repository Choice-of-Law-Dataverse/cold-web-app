<template>
  <div class="flex flex-col gap-4 md:flex-row md:items-start md:gap-6">
    <div class="label-key md:w-48 md:flex-shrink-0">
      <span class="flex items-center">
        {{ label }}
        <slot name="label-actions" />
        <InfoPopover v-if="tooltip" :text="tooltip" />
      </span>
    </div>

    <div class="md:flex-1">
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
.label-key {
  padding: 0;
}

.label-key span {
  display: inline-flex;
  align-items: center;
}
</style>
