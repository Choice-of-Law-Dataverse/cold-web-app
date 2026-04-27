<template>
  <LinkChipNeutral
    v-if="variant === 'chip'"
    :class="['entity-link', { 'entity-link--cmd': isModKeyHeld }]"
    :href="href"
    @click="handleClick"
  >
    <slot>{{ title }}</slot>
    <span
      v-if="badge"
      class="entity-link__badge"
      :style="{
        backgroundColor: `color-mix(in srgb, ${badge.color} 14%, white)`,
        color: badge.color,
      }"
    >
      {{ badge.label }}
    </span>
    <span
      class="entity-link__icon entity-link__icon--panel"
      aria-hidden="true"
    />
    <span
      class="entity-link__icon entity-link__icon--arrow"
      aria-hidden="true"
    />
  </LinkChipNeutral>
  <a
    v-else
    :class="[
      'entity-link',
      'entity-link--jurisdiction',
      { 'entity-link--cmd': isModKeyHeld },
    ]"
    :href="href"
    @click="handleClick"
  >
    <slot>{{ title }}</slot>
    <span
      v-if="badge"
      class="entity-link__badge"
      :style="{
        backgroundColor: `color-mix(in srgb, ${badge.color} 14%, white)`,
        color: badge.color,
      }"
    >
      {{ badge.label }}
    </span>
    <span
      class="entity-link__icon entity-link__icon--panel"
      aria-hidden="true"
    />
    <span
      class="entity-link__icon entity-link__icon--arrow"
      aria-hidden="true"
    />
  </a>
</template>

<script setup lang="ts">
import { useModKeyState } from "@/composables/useModKeyState";
import { useEntityDrawer } from "@/composables/useEntityDrawer";
import { getEntityConfig } from "@/config/entityRegistry";
import LinkChipNeutral from "@/components/ui/LinkChipNeutral.vue";
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    id: string;
    title: string;
    basePath: string;
    badge?: {
      label: string;
      color: string;
    };
    variant?: "chip" | "jurisdiction";
  }>(),
  {
    badge: undefined,
    variant: "chip",
  },
);

const { isModKeyHeld } = useModKeyState();
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

<style scoped>
.entity-link:not(.entity-link--jurisdiction)::after {
  display: none;
}

.entity-link__badge {
  display: inline-flex;
  align-items: center;
  border-radius: 9999px;
  padding: 0.0625rem 0.4rem;
  font-size: 0.625rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  line-height: 1.125rem;
  white-space: nowrap;
  margin-left: 0.25rem;
  vertical-align: middle;
}

.entity-link__icon {
  display: inline-block;
  width: 0;
  height: 12px;
  margin-left: 0;
  background-color: currentColor;
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
  -webkit-mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  opacity: 0;
  transition:
    width 0.2s ease,
    margin-left 0.2s ease,
    opacity 0.15s ease;
}

.entity-link__icon--panel {
  mask-image: var(--icon-panel-right);
  -webkit-mask-image: var(--icon-panel-right);
}

.entity-link__icon--arrow {
  mask-image: var(--icon-arrow-right);
  -webkit-mask-image: var(--icon-arrow-right);
}

.entity-link:hover .entity-link__icon--panel {
  width: 1rem;
  opacity: 1;
}

.entity-link--cmd:hover .entity-link__icon--panel {
  width: 0;
  opacity: 0;
}

.entity-link--cmd:hover .entity-link__icon--arrow {
  width: 1rem;
  opacity: 1;
}

@media (pointer: coarse) {
  .entity-link:active .entity-link__icon--arrow {
    width: 1rem;
    opacity: 1;
  }

  .entity-link .entity-link__icon--panel {
    display: none;
  }
}

.entity-link--jurisdiction {
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  color: var(--color-cold-night);
  letter-spacing: 0.05em;
  display: flex;
  cursor: pointer;
  align-items: center;
  border-radius: 0.5rem;
  text-align: left;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  transition:
    box-shadow 150ms ease,
    background 150ms ease,
    color 150ms ease;
  background: var(--gradient-subtle);
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
}

.entity-link--jurisdiction:hover {
  box-shadow:
    0 1px 3px 0 rgb(0 0 0 / 0.1),
    0 1px 2px -1px rgb(0 0 0 / 0.1);
  background: var(--gradient-subtle-emphasis);
}

.entity-link--jurisdiction:focus-visible {
  outline: 2px solid var(--color-cold-purple);
  outline-offset: 2px;
}

.entity-link--jurisdiction :deep(.flag-wrapper) {
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

.entity-link--jurisdiction:hover :deep(.flag-wrapper) {
  width: 0;
  opacity: 0;
  overflow: hidden;
}

.entity-link--jurisdiction::after {
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

.entity-link--jurisdiction:hover::after {
  width: 1rem;
  opacity: 1;
}

.entity-link--jurisdiction :deep(.item-flag) {
  height: auto;
}

.entity-link--jurisdiction :deep(span) {
  color: var(--color-cold-night);
}

.entity-link--jurisdiction :deep(.item-icon) {
  flex-shrink: 0;
  font-size: 1.25rem;
  transition: color 150ms;
  color: var(--color-cold-green);
}

.entity-link--jurisdiction:hover :deep(.item-icon) {
  color: color-mix(in srgb, var(--color-cold-green) 85%, #000);
}

.entity-link--jurisdiction:hover .entity-link__icon {
  color: var(--color-cold-purple);
}
</style>
