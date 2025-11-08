<template>
  <a
    href="https://creativecommons.org/licenses/by-sa/4.0/"
    target="_blank"
    rel="noopener noreferrer"
    class="label-open-science"
    style="display: inline-flex; text-decoration: none"
    title="This is an Open Science project. Content is freely available under CC BY-SA 4.0 license."
  >
    <UIcon
      name="i-material-symbols:public"
      class="mr-[0.3em] mt-[0.1em] text-[1.15em]"
    />
    <span class="desktop-only-text">Open Science • </span>CC BY-SA
  </a>
</template>

<style scoped>
.label-open-science {
  color: var(--color-cold-night);
  background-color: var(--color-cold-purple-alpha);
  border: 1px solid var(--color-cold-night);
  padding: 0.375rem 0.75rem;
}
@media (max-width: 639px) {
  .label-open-science {
    padding: 0.375rem 0.5rem;
  }
  .desktop-only-text {
    display: none;
  }
}
</style>
