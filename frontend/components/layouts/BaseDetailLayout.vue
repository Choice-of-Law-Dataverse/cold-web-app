<template>
  <DetailDisplay
    :loading="props.loading"
    :result-data="props.resultData"
    :key-label-pairs="computedKeyLabelPairs"
    :value-class-map="{}"
    :formatted-source-table="props.sourceTable"
    :formatted-jurisdiction="props.formattedJurisdiction"
    :show-header="props.showHeader"
    :show-open-link="props.showOpenLink"
    :show-suggest-edit="props.showSuggestEdit"
    :formatted-theme="props.formattedTheme"
    :header-mode="props.headerMode"
    :show-notification-banner="props.showNotificationBanner"
    :notification-banner-message="props.notificationBannerMessage"
    :fallback-message="props.fallbackMessage"
    :icon="props.icon"
    @save="emit('save')"
    @open-save-modal="emit('open-save-modal')"
    @open-cancel-modal="emit('open-cancel-modal')"
  >
    <slot />
    <template v-for="(_, name) in $slots" :key="name" #[name]="slotData">
      <slot :name="name" v-bind="slotData" />
    </template>
  </DetailDisplay>
</template>

<script setup lang="ts" generic="T extends object">
import { computed } from "vue";
import DetailDisplay from "@/components/ui/BaseDetailDisplay.vue";

const props = withDefaults(
  defineProps<{
    loading: boolean;
    resultData: T;
    // Label/tooltip maps - keys must match T
    labels?: Partial<Record<keyof T, string>>;
    tooltips?: Partial<Record<keyof T, string>>;
    // Legacy props (deprecated, used for index pages with full-width slot)
    keyLabelPairs?: Record<string, unknown>[];
    sourceTable: string;
    formattedJurisdiction?: Record<string, unknown>[];
    showHeader?: boolean;
    formattedTheme?: Record<string, unknown>[];
    headerMode?: string;
    showNotificationBanner?: boolean;
    notificationBannerMessage?: string;
    fallbackMessage?: string;
    icon?: string;
    showOpenLink?: boolean;
    showSuggestEdit?: boolean;
  }>(),
  {
    labels: () => ({}),
    tooltips: undefined,
    keyLabelPairs: undefined,
    formattedJurisdiction: () => [],
    showHeader: true,
    formattedTheme: () => [],
    headerMode: "default",
    notificationBannerMessage: "",
    fallbackMessage: "",
    icon: "",
    showOpenLink: false,
    showSuggestEdit: false,
  },
);

const emit = defineEmits(["save", "open-save-modal", "open-cancel-modal"]);

// Convert typed props to legacy format for BaseDetailDisplay
// Fields are derived from labels keys (order preserved in modern JS)
const computedKeyLabelPairs = computed(() => {
  // If labels are provided, derive fields from them
  if (props.labels && Object.keys(props.labels).length > 0) {
    const tooltips = props.tooltips as Record<string, string> | undefined;
    return Object.entries(props.labels).map(([key, label]) => ({
      key,
      label,
      tooltip: tooltips?.[key],
      emptyValueBehavior: { action: "hide" },
    }));
  }
  // Fallback to keyLabelPairs for legacy index pages
  return props.keyLabelPairs ?? [];
});
</script>
