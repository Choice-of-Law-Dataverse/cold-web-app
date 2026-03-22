<template>
  <UTooltip
    text="Compliant with Hague Conference on Private International Law standards"
  >
    <NuxtLink
      to="/about/endorsements"
      class="label-hcch"
      style="display: inline-flex; text-decoration: none"
    >
      <UIcon
        name="i-material-symbols:check-circle"
        class="mt-[0.1em] mr-[0.3em] text-[1.15em]"
      />
      HCCH&nbsp;Compliant
    </NuxtLink>
  </UTooltip>
</template>

<style scoped>
.label-hcch {
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: inline-flex;
  gap: 4px;
  padding: 4px 10px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  border-radius: 4px;
  color: var(--color-cold-night);
  background-color: var(--color-cold-green);
  border: 1px solid var(--color-cold-night);
  transition: all 0.15s ease;
}
</style>
