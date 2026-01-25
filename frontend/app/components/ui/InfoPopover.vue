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
    <span class="icon cursor-pointer px-1">
      <Icon name="i-material-symbols:info-outline" />
    </span>

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
