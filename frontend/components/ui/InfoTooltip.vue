<template>
  <UTooltip
    :popper="{ placement }"
    :ui="{
      background: 'bg-cold-night',
      color: 'text-white',
      base: 'pt-3 pr-3 pb-3 pl-3 normal-case whitespace-normal h-auto',
      rounded: 'rounded-none',
      ring: '',
    }"
  >
    <span class="icon-span ml-1 cursor-pointer">
      <Icon name="i-material-symbols:info-outline" />
    </span>
    <template #text>
      <span class="tooltip-text" v-html="text" />
    </template>
  </UTooltip>
</template>

<script setup>
const props = defineProps({
  text: {
    type: String,
    required: true,
  },
  placement: {
    type: String,
    default: 'top',
  },
})
</script>

<style scoped>
.icon-span {
  display: inline-flex;
  align-items: center;
  margin-top: -1px;
  color: var(--color-cold-purple);
  font-size: 1.1em;
}

/* Ensure tooltip text is white and in one column */
.tooltip-text {
  color: white;
  display: block;
  white-space: normal;
}
</style>
