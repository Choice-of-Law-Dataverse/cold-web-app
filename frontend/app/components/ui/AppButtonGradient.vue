<template>
  <UButton
    color="primary"
    variant="solid"
    class="app-btn-gradient"
    v-bind="$attrs"
  >
    <template v-for="(_, name) in $slots" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps ?? {}" />
    </template>
  </UButton>
</template>

<style>
@reference "@/assets/styles.css";

.app-btn-gradient {
  background-image: linear-gradient(
    to right,
    var(--color-cold-purple),
    color-mix(in srgb, var(--color-cold-purple) 90%, transparent)
  );
  --btn-shadow: 0 10px 15px -3px rgba(111, 77, 250, 0.25);
  box-shadow: var(--btn-shadow);
  @apply transition-shadow duration-150;
}

.app-btn-gradient:hover:not(:disabled) {
  --btn-shadow: 0 20px 25px -5px rgba(111, 77, 250, 0.3);
  box-shadow: var(--btn-shadow);
}

.app-btn-gradient:disabled {
  @apply opacity-60;
}
</style>
