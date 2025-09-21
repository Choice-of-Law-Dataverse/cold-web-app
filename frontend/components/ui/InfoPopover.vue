<template>
  <UPopover
    :popper="{ placement }"
    :ui="{
      background: 'bg-cold-night',
      ring: '',
      rounded: 'rounded-none',
      shadow: 'shadow-lg',
      base: 'overflow-hidden',
    }"
  >
    <span class="icon cursor-pointer p-2">
      <Icon name="i-material-symbols:info-outline" />
    </span>

    <template #panel>
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
  color: var(--color-cold-purple);
}

.content {
  background-color: var(--color-cold-night);
  color: white;
  text-transform: none;
}
</style>
