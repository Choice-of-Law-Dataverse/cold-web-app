<template>
  <div
    :key="`${resolvedJurisdiction.join()}-${resolvedTheme.join()}-${legalFamily.join()}`"
    class="header-container flex flex-wrap items-center justify-between gap-3"
  >
    <template v-if="cardType === 'Loading'" />
    <template v-else>
      <div
        v-if="showSuggestEdit && headerMode !== 'new'"
        class="order-last sm:hidden"
      >
        <UDropdownMenu :items="mobileMenuItems">
          <UButton
            icon="i-material-symbols:more-vert"
            variant="ghost"
            color="neutral"
            size="sm"
          />
        </UDropdownMenu>
      </div>

      <CardTags
        :formatted-jurisdiction="resolvedJurisdiction"
        :formatted-theme="resolvedTheme"
        :legal-family="legalFamily"
        :source-table-label="adjustedSourceTable"
        :label-color-class="labelColorClass"
        :header-mode="headerMode"
      />

      <CardActions
        :result-data="resultData"
        :card-type="formattedSourceTable"
        :show-suggest-edit="showSuggestEdit"
        :show-open-link="showOpenLink"
        :header-mode="headerMode"
        @open-save-modal="emit('open-save-modal')"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import {
  parseJurisdictionString,
  primaryJurisdictionAlpha3,
} from "@/utils/jurisdictionParser";
import { getSingularLabel, getLabelColorClass } from "@/config/entityRegistry";
import { useJurisdictionLookup } from "@/composables/useJurisdictions";
import CardTags from "@/components/ui/CardTags.vue";
import CardActions from "@/components/ui/CardActions.vue";

const emit = defineEmits<{
  save: [];
  "open-save-modal": [];
  "open-cancel-modal": [];
}>();

const props = withDefaults(
  defineProps<{
    resultData: Record<string, unknown>;
    cardType: string;
    showSuggestEdit?: boolean;
    showOpenLink?: boolean;
    formattedJurisdiction?: string[];
    formattedTheme?: string[];
    headerMode?: string;
  }>(),
  {
    showSuggestEdit: true,
    showOpenLink: true,
    formattedJurisdiction: () => [],
    formattedTheme: () => [],
    headerMode: "default",
  },
);

const { findJurisdictionByCode } = useJurisdictionLookup();

const primaryJurisdictionCode = computed(() =>
  primaryJurisdictionAlpha3(props.resultData),
);

const resolvedJurisdiction = computed(() => {
  if (props.formattedJurisdiction.length > 0) {
    return props.formattedJurisdiction;
  }
  const jurisdictionString = String(
    props.resultData.jurisdictionName ||
      props.resultData.jurisdictionNames ||
      props.resultData.nameFromJurisdiction ||
      props.resultData.jurisdiction ||
      props.resultData.jurisdictions ||
      props.resultData.instrument ||
      "",
  );

  const parsed = jurisdictionString
    ? parseJurisdictionString(jurisdictionString)
    : [];
  if (parsed.length === 1) return parsed;

  const primary = findJurisdictionByCode(primaryJurisdictionCode.value);
  if (primary?.name) {
    if (parsed.length === 0) return [primary.name];
    const match = parsed.find(
      (name) => name.toLowerCase() === primary.name.toLowerCase(),
    );
    if (match) return [match];
  }
  return [];
});

const formattedSourceTable = computed(() => {
  return props.cardType || String(props.resultData?.sourceTable ?? "");
});

const adjustedSourceTable = computed(() =>
  getSingularLabel(formattedSourceTable.value),
);

const labelColorClass = computed(() =>
  getLabelColorClass(formattedSourceTable.value),
);

const resolvedTheme = computed(() => {
  if (props.formattedTheme.length > 0) {
    return props.formattedTheme;
  }

  if (props.cardType === "Literature" && props.resultData.themes) {
    return String(props.resultData.themes)
      .split(/[,|]/)
      .map((theme: string) => theme.trim())
      .filter((t) => t && t !== "null" && t !== "None");
  }

  const themes =
    props.resultData.titleOfTheProvision ?? props.resultData.themes;

  if (!themes || themes === "None" || themes === "null") {
    return [];
  }

  return [
    ...new Set(
      String(themes)
        .split(/[,|]/)
        .map((theme: string) => theme.trim())
        .filter((t) => t && t !== "null" && t !== "None"),
    ),
  ];
});

const legalFamily = computed(() => {
  if (
    props.resultData &&
    (props.cardType === "Jurisdiction" || props.resultData.legalFamily)
  ) {
    const value = String(props.resultData.legalFamily || "");
    if (!value || value === "N/A") return [];
    return value
      .split(",")
      .map((f: string) => f.trim())
      .filter((f: string) => f);
  }
  return [];
});

const mobileMenuItems = computed(() => {
  return [
    [
      {
        label: "Cite",
        icon: "i-material-symbols:verified-outline",
        onSelect: () => {},
      },
      {
        label: "Export JSON",
        icon: "i-material-symbols:data-object",
        onSelect: () => {},
      },
      {
        label: "Print",
        icon: "i-material-symbols:print-outline",
        onSelect: () => {
          window.print();
        },
      },
    ],
  ];
});
</script>

<style scoped>
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.gray-link {
  color: var(--color-cold-night-alpha-25);
}

:deep(.mobile-menu-item) {
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-cold-night);
  cursor: pointer;
  transition: all 0.15s ease;
  border-left: 2px solid transparent;
}

:deep(.mobile-menu-item:hover),
:deep(.mobile-menu-item-active) {
  background: var(--gradient-subtle);
  color: var(--color-cold-purple);
  border-left-color: var(--color-cold-purple);
}
</style>
