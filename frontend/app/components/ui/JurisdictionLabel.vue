<template>
  <NuxtLink :to="href" class="jurisdiction-label" @click.prevent="handleClick">
    <slot />
  </NuxtLink>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useEntityDrawer } from "@/composables/useEntityDrawer";
import { getEntityConfig } from "@/config/entityRegistry";

const props = defineProps<{
  id: string;
  basePath: string;
}>();

const { openDrawer } = useEntityDrawer();

const href = computed(() =>
  props.id.startsWith("/") ? props.id : `${props.basePath}/${props.id}`,
);

function handleClick(event: MouseEvent) {
  if (event.metaKey || event.ctrlKey) return;

  const config = getEntityConfig(props.basePath);
  if (!config) return;

  event.preventDefault();
  const forceDrawer = config.hasDetailPage === false;
  openDrawer(props.id, config.table, props.basePath, forceDrawer);
}
</script>

<style>
@reference "tailwindcss";

.jurisdiction-label {
  @apply inline-flex cursor-pointer items-center gap-2 text-left;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-cold-night);
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  background: var(--gradient-subtle);
  padding: 0.25rem 0.5rem;
  text-decoration: none;
  transition:
    box-shadow 150ms ease,
    background 150ms ease,
    color 150ms ease;
}

.jurisdiction-label:hover {
  box-shadow:
    0 1px 3px 0 rgb(0 0 0 / 0.1),
    0 1px 2px -1px rgb(0 0 0 / 0.1);
  background: var(--gradient-subtle-emphasis);
}

.jurisdiction-label:focus-visible {
  outline: 2px solid var(--color-cold-purple);
  outline-offset: 2px;
}

.jurisdiction-label .flag-wrapper {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 1rem;
  overflow: hidden;
  transition:
    width 0.2s ease,
    opacity 0.15s ease;
}

.jurisdiction-label:hover .flag-wrapper {
  width: 0;
  opacity: 0;
  overflow: hidden;
}

.jurisdiction-label::after {
  content: "";
  display: inline-block;
  width: 0;
  height: 1rem;
  background-color: currentColor;
  mask-image: var(--icon-arrow-right);
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
  -webkit-mask-image: var(--icon-arrow-right);
  -webkit-mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  opacity: 0;
  transition:
    width 0.2s ease,
    opacity 0.15s ease;
}

.jurisdiction-label:hover::after {
  width: 1rem;
  opacity: 1;
}

.jurisdiction-label .item-flag {
  height: auto;
}

.jurisdiction-label span {
  color: var(--color-cold-night);
}

.jurisdiction-label .item-icon {
  flex-shrink: 0;
  font-size: 1.25rem;
  transition: color 150ms;
  color: var(--color-cold-green);
}

.jurisdiction-label:hover .item-icon {
  color: color-mix(in srgb, var(--color-cold-green) 85%, #000);
}
</style>
