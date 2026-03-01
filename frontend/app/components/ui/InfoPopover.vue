<template>
  <UPopover
    :popper="{ placement }"
    :ui="{
      background: 'bg-cold-night',
      ring: '',
      rounded: 'rounded-lg',
      shadow: 'shadow-lg',
      base: 'overflow-hidden',
    }"
  >
    <button
      type="button"
      class="icon cursor-pointer px-1"
      aria-label="More information"
    >
      <Icon name="i-material-symbols:info-outline" />
    </button>

    <template #content>
      <div class="content p-3">
        {{ text }}
      </div>
    </template>
  </UPopover>
</template>

<script setup>
defineProps({
  text: {
    type: String,
    required: true,
  },
  placement: {
    type: String,
    default: "top",
  },
});
</script>

<style scoped>
.icon {
  color: var(--color-cold-teal);
}

.content {
  background-color: var(--color-cold-teal);
  color: white;
  text-transform: none;
  max-width: 52ch;
}
</style>
