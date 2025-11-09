<template>
  <NuxtLink
    to="/disclaimer"
    class="label-open-science fit-content inline-flex items-center gap-1 px-1 py-0.5 no-underline"
    title="This is an Open Science project. Content is freely available under CC BY-SA 4.0 license."
  >
    <UIcon name="i-material-symbols:public" />
    <span>Open&nbsp;Science</span></NuxtLink
  >
</template>

<style scoped>
.label-open-science {
  color: var(--color-cold-teal);
  background-color: var(--color-cold-purple-alpha);
  border: 1px solid var(--color-cold-night-alpha);
  font-size: 0.75rem;
  text-transform: uppercase;
  font-variant: small-caps;
}
</style>
