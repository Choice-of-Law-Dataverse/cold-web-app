<template>
  <a :class="['label-link', kind === 'jurisdiction' && 'label-jurisdiction']"
    ><slot
  /></a>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    kind?: "default" | "jurisdiction";
  }>(),
  { kind: "default" },
);
</script>

<style>
@reference "@/assets/styles.css";

.label-link {
  @apply relative inline-flex items-center gap-0 font-medium no-underline;
  @apply pr-4;
  transition:
    color 0.15s ease,
    padding-right 0.2s ease;
}

.label-link:hover {
  @apply pr-0;
}

.label-link::after {
  content: "";
  @apply inline-block;
  width: 0;
  height: 12px;
  margin-left: 0;
  background-color: currentColor;
  mask-image: var(--icon-search);
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
  -webkit-mask-image: var(--icon-search);
  -webkit-mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  opacity: 0;
  transition:
    width 0.2s ease,
    margin-left 0.2s ease,
    opacity 0.15s ease;
}

.label-link:hover::after {
  width: 12px;
  margin-left: 4px;
  opacity: 1;
}

.label-link.label-jurisdiction {
  color: var(--color-cold-night);
}

.label-link.label-jurisdiction:hover {
  color: var(--color-cold-purple);
}
</style>
