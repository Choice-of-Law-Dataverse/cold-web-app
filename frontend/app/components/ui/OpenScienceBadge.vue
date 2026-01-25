<template>
  <UTooltip
    text="Open Science project - Content freely available under CC BY-SA 4.0 license"
  >
    <NuxtLink
      to="/disclaimer"
      class="label-open-science fit-content inline-flex items-center gap-1 px-1 py-0.5 no-underline"
    >
      <UIcon
        class="text-[1.15em]"
        name="i-material-symbols:copyright-outline"
        :style="{ transform: 'rotate(180deg)' }"
      />
      <span>Open&nbsp;Science</span></NuxtLink
    >
  </UTooltip>
</template>

<style scoped>
.label-open-science {
  color: var(--color-cold-night);
  background-color: var(--color-cold-green);
  border: 1px solid var(--color-cold-night);
  font-size: 0.75rem;
  text-transform: uppercase;
  font-variant: small-caps;
}
</style>
