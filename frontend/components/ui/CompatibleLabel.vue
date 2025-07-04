<template>
  <span
    class="label-question"
    style="display: inline-flex; width: 126px; align-items: center"
  >
    <UIcon name="i-material-symbols:balance" class="text-[3em] mr-2" />
    {{ label }}
  </span>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    default: 'Your fav Law',
  },
})
</script>

<style scoped>
.label-question {
  color: var(--color-cold-night);
  background-color: var(--color-cold-green-alpha);
  border: 1px solid var(--color-cold-green);
  line-height: 1.2em;
}
</style>
