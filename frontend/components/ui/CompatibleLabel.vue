<template>
  <span
    class="label-question"
    style="display: inline-flex; width: 126px; align-items: center"
  >
    <UIcon name="i-material-symbols:balance" class="icon-fixed mr-2" />
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
  background-color: var(--color-cold-green-alpha-10);
  border: 1px solid var(--color-cold-green);
  line-height: 1.2em;
  padding-top: 0.5em;
  padding-bottom: 0.4em;
}
.icon-fixed {
  font-size: 1.7em;
  width: 1.2em;
  height: 1.2em;
  min-width: 1.2em;
  min-height: 1.2em;
  max-width: 1.2em;
  max-height: 1.2em;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>
