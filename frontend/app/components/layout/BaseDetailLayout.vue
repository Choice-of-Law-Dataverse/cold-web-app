<template>
  <DetailDisplay
    :loading="props.loading"
    :error="props.error ?? undefined"
    :result-data="props.data"
    :key-label-pairs="computedKeyLabelPairs"
    :value-class-map="{}"
    :formatted-source-table="props.table"
    :formatted-jurisdiction="props.formattedJurisdiction"
    :formatted-theme="props.formattedTheme"
    :show-suggest-edit="props.showSuggestEdit"
    :header-mode="props.headerMode"
    :show-notification-banner="props.showNotificationBanner"
    :notification-banner-message="props.notificationBannerMessage"
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

<script setup lang="ts" generic="T extends TableName">
import { computed } from "vue";
import type { TableName, TableProcessedMap } from "@/types/api";
import DetailDisplay from "@/components/ui/DetailDisplay.vue";

const props = withDefaults(
  defineProps<{
    table: T;
    loading: boolean;
    error?: Error | null;
    // Data accepts typed processed response or empty object for legacy/new pages
    data: TableProcessedMap[T] | Record<string, unknown>;
    // Label/tooltip maps - keys must match the table's processed type
    labels?: Partial<Record<keyof TableProcessedMap[T], string>>;
    tooltips?: Partial<Record<keyof TableProcessedMap[T], string>>;
    // Legacy props for index pages with full-width slot
    keyLabelPairs?: Record<string, unknown>[];
    // Props passed to child components
    formattedJurisdiction?: Record<string, unknown>[];
    formattedTheme?: Record<string, unknown>[];
    headerMode?: string;
    showNotificationBanner?: boolean;
    notificationBannerMessage?: string;
    icon?: string;
    showSuggestEdit?: boolean;
  }>(),
  {
    error: undefined,
    labels: () => ({}),
    tooltips: undefined,
    keyLabelPairs: undefined,
    formattedJurisdiction: () => [],
    formattedTheme: () => [],
    headerMode: "default",
    notificationBannerMessage: "",
    icon: "",
    showSuggestEdit: false,
  },
);

const emit = defineEmits(["save", "open-save-modal", "open-cancel-modal"]);

// Convert typed props to legacy format for DetailDisplay
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
