<template>
  <div
    class="entity-filters"
    :class="{ 'entity-filters--loading': props.loading }"
    :aria-busy="props.loading || undefined"
  >
    <div
      v-if="props.filters.includes('jurisdiction')"
      class="entity-filters__control"
    >
      <JurisdictionSelectMenu
        v-if="jurisdictions"
        :jurisdictions="jurisdictions"
        :model-value="jurisdiction"
        placeholder="Jurisdiction"
        @update:model-value="jurisdiction = $event"
      />
    </div>

    <div v-if="props.filters.includes('theme')" class="entity-filters__control">
      <USelectMenu
        v-model="theme"
        :items="themeOptions"
        placeholder="Theme"
        size="xl"
        class="w-56"
        :ui="{
          content:
            'max-h-(--reka-combobox-content-available-height) w-max min-w-(--reka-combobox-trigger-width)',
          item: 'data-highlighted:bg-transparent',
        }"
      >
        <template #item-label="{ item }">
          <span class="schip schip--theme schip--static">
            <span class="schip-tag" aria-hidden="true">
              <UIcon name="i-lucide:bookmark" />
            </span>
            <span class="schip-text">{{ item }}</span>
          </span>
        </template>
      </USelectMenu>
    </div>

    <div v-if="hasActiveFilter" class="entity-filters__reset">
      <span
        v-if="props.loading"
        class="entity-filters__status"
        role="status"
        aria-live="polite"
      >
        <span class="entity-filters__pulse" aria-hidden="true" />
        Updating
      </span>
      <span v-else-if="formattedCount" class="entity-filters__count">
        {{ formattedCount }} {{ count === 1 ? "result" : "results" }}
      </span>
      <UButton
        variant="ghost"
        size="sm"
        :leading-icon="ICON_CLEAR"
        :trailing-icon="ICON_CLEAR"
        :disabled="props.loading"
        @click="reset"
      >
        Clear filters
      </UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import JurisdictionSelectMenu from "@/components/jurisdiction/JurisdictionSelectMenu.vue";
import { useJurisdictions } from "@/composables/useJurisdictions";
import themeOptions from "@/assets/themeOptions.json";
import type { JurisdictionOption } from "@/types/analyzer";

export type EntityListFilterKey = "jurisdiction" | "theme";

const ICON_CLEAR = "i-material-symbols:close";

const props = defineProps<{
  filters: EntityListFilterKey[];
  count?: number;
  loading?: boolean;
}>();

const jurisdiction = defineModel<JurisdictionOption | undefined>(
  "jurisdiction",
);
const theme = defineModel<string | undefined>("theme");

const wantsJurisdiction = computed(() =>
  props.filters.includes("jurisdiction"),
);
const { data: jurisdictions } = useJurisdictions(wantsJurisdiction);

const hasActiveFilter = computed(
  () => Boolean(jurisdiction.value?.coldId) || Boolean(theme.value),
);

const formattedCount = computed(() =>
  typeof props.count === "number"
    ? props.count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "'")
    : "",
);

const reset = () => {
  jurisdiction.value = undefined;
  theme.value = undefined;
};
</script>

<style scoped>
.entity-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.entity-filters__control {
  min-width: 14rem;
  transition: opacity 200ms ease;
}

.entity-filters--loading .entity-filters__control {
  opacity: 0.55;
  pointer-events: none;
}

.entity-filters__reset {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.entity-filters__count {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-cold-night-alpha);
}

.entity-filters__status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-family: "IBM Plex Mono", monospace;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-cold-night-alpha);
}

.entity-filters__pulse {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--color-cold-purple);
  animation: entity-filters-pulse 1.1s ease-in-out infinite;
  box-shadow: 0 0 0 0
    color-mix(in srgb, var(--color-cold-purple) 30%, transparent);
}

@keyframes entity-filters-pulse {
  0%,
  100% {
    transform: scale(0.55);
    opacity: 0.45;
    box-shadow: 0 0 0 0
      color-mix(in srgb, var(--color-cold-purple) 30%, transparent);
  }
  50% {
    transform: scale(1);
    opacity: 1;
    box-shadow: 0 0 0 4px
      color-mix(in srgb, var(--color-cold-purple) 0%, transparent);
  }
}

@media (prefers-reduced-motion: reduce) {
  .entity-filters__control {
    transition: none;
  }
  .entity-filters__pulse {
    animation: none;
    opacity: 0.85;
  }
}
</style>
