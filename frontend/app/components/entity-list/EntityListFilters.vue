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
        }"
      />
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
</style>
