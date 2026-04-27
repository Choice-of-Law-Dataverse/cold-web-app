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
      'label-jurisdiction',
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
.entity-link::after {
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

.entity-link.label-jurisdiction:hover .entity-link__icon {
  color: var(--color-cold-purple);
}
</style>
