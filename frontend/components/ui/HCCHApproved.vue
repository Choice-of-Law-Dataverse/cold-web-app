<template>
  <UTooltip
    text="Compliant with Hague Conference on Private International Law standards"
  >
    <NuxtLink
      to="/about/endorsements"
      class="label-question"
      style="display: inline-flex; text-decoration: none"
    >
      <UIcon
        name="i-material-symbols:check-circle"
        class="mr-[0.3em] mt-[0.1em] text-[1.15em]"
      />
      HCCH&nbsp;Compliant
    </NuxtLink>
  </UTooltip>
</template>

<style scoped>
.label-question {
  color: var(--color-cold-night);
  background-color: var(--color-cold-green);
  border: 1px solid var(--color-cold-night);
}
</style>
