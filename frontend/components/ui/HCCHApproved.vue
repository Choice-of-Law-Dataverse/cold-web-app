<template>
  <a
    href="/about/endorsements"
    class="label-question"
    style="display: inline-flex; text-decoration: none"
  >
    <UIcon
      name="i-material-symbols:check-circle"
      class="mr-[0.3em] text-[1.15em] mt-[0.1em]"
    />
    HCCH<span class="desktop-only-text">&nbsp;Compliant</span>
  </a>
</template>

<style scoped>
.label-question {
  color: var(--color-cold-night);
  background-color: var(--color-cold-green);
  border: 1px solid var(--color-cold-night);
}
@media (max-width: 639px) {
  .label-question {
    padding-right: 9px !important;
  }
  .desktop-only-text {
    display: none;
  }
}
</style>
