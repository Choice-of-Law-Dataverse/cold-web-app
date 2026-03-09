<template>
  <div
    :key="`${formattedJurisdiction.join()}-${formattedTheme.join()}-${legalFamily.join()}`"
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
        :formatted-jurisdiction="formattedJurisdiction"
        :formatted-theme="formattedTheme"
        :legal-family="legalFamily"
        :source-table-label="adjustedSourceTable"
        :label-color-class="labelColorClass"
        :header-mode="headerMode"
      />

      <CardActions
        :result-data="resultData"
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
import { parseJurisdictionString } from "@/utils/jurisdictionParser";
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

const formattedJurisdiction = computed(() => {
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

  if (!jurisdictionString) {
    return [];
  }

  const parsed = parseJurisdictionString(jurisdictionString);
  if (parsed.length > 1) return [];
  return parsed;
});

const formattedSourceTable = computed(() => {
  return props.cardType || String(props.resultData?.sourceTable ?? "");
});

const adjustedSourceTable = computed(() => {
  switch (formattedSourceTable.value) {
    case "Court Decisions":
      return "Court Decision";
    case "Answers":
      return "Question";
    case "Domestic Instrument":
      return "Domestic Instrument";
    case "Regional Instrument":
      return "Regional Instrument";
    case "International Instrument":
      return "International Instrument";
    case "Literature":
      return "Literature";
    case "Arbitral Rule":
      return "Arbitral Rule";
    case "Arbitral Award":
      return "Arbitral Award";
    case "Jurisdiction":
    case "Jurisdictions":
      return "Jurisdiction";
    default:
      return formattedSourceTable.value || "";
  }
});

const labelColorClass = computed(() => {
  switch (formattedSourceTable.value) {
    case "Court Decisions":
    case "Court Decision":
      return "label-court-decision";
    case "Answers":
    case "Question":
      return "label-question";
    case "Domestic Instrument":
    case "Regional Instrument":
    case "International Instrument":
      return "label-instrument";
    case "Arbitral Rule":
    case "Arbitral Award":
      return "label-arbitration";
    case "Literature":
      return "label-literature";
    case "Jurisdiction":
      return "hidden";
    default:
      return "";
  }
});

const formattedTheme = computed(() => {
  if (props.formattedTheme.length > 0) {
    return props.formattedTheme;
  }

  if (props.cardType === "Literature" && props.resultData.themes) {
    return String(props.resultData.themes)
      .split(",")
      .map((theme: string) => theme.trim());
  }

  const themes =
    props.resultData.titleOfTheProvision ?? props.resultData.themes;

  if (!themes || themes === "None") {
    return [];
  }

  return [
    ...new Set(
      String(themes)
        .split(",")
        .map((theme: string) => theme.trim()),
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
