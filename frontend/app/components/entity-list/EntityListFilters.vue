<template>
  <div class="entity-filters">
    <div
      v-if="props.filters.includes('jurisdiction')"
      class="entity-filters__control"
    >
      <label class="entity-filters__label">Jurisdiction</label>
      <JurisdictionSelectMenu
        v-if="jurisdictions"
        :jurisdictions="jurisdictions"
        :model-value="jurisdiction"
        placeholder="Any"
        @update:model-value="jurisdiction = $event"
      />
    </div>

    <div v-if="props.filters.includes('theme')" class="entity-filters__control">
      <label class="entity-filters__label">Theme</label>
      <USelectMenu
        v-model="theme"
        :items="themeOptions"
        placeholder="Any"
        size="xl"
        class="w-56"
        :ui="{
          content: 'max-h-none w-max min-w-(--reka-combobox-trigger-width)',
          item: 'data-highlighted:bg-transparent',
        }"
      >
        <template #item-label="{ item }">
          <span class="schip schip--theme">
            <span class="schip-tag" aria-hidden="true">
              <UIcon name="i-lucide:bookmark" />
            </span>
            <span class="schip-text">{{ item }}</span>
          </span>
        </template>
      </USelectMenu>
    </div>

    <div v-if="hasActiveFilter" class="entity-filters__reset">
      <UButton variant="ghost" size="sm" :icon="ICON_CLEAR" @click="reset">
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
}

.entity-filters__label {
  display: block;
  font-weight: 700;
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-cold-night-alpha);
  margin-bottom: 4px;
}

.entity-filters__reset {
  display: flex;
  align-items: flex-end;
}

.schip {
  --schip-color: var(--color-cold-purple);
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-family: "IBM Plex Mono", monospace;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 2px 9px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--schip-color) 8%, white);
  color: color-mix(in srgb, var(--schip-color) 80%, black);
  white-space: nowrap;
  border: 1px solid transparent;
}

.schip--theme {
  --schip-color: var(--color-cold-purple);
}

.schip-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 11px;
  font-size: 11px;
  opacity: 0.65;
}
</style>
