<template>
  <DetailDisplay
    :loading="props.loading"
    :error="props.error ?? undefined"
    :result-data="resultDataForDisplay"
    :key-label-pairs="keyLabelPairsForDisplay"
    :value-class-map="{}"
    :formatted-source-table="props.table"
    :formatted-jurisdiction="props.formattedJurisdiction"
    :formatted-theme="props.formattedTheme"
    :show-header="true"
    :show-open-link="false"
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
    data: TableProcessedMap[T] | Record<string, unknown>;
    labels?: Partial<Record<keyof TableProcessedMap[T], string>>;
    tooltips?: Partial<Record<keyof TableProcessedMap[T], string>>;
    keyLabelPairs?: Record<string, unknown>[];
    formattedJurisdiction?: string[];
    formattedTheme?: string[];
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
    showNotificationBanner: false,
    notificationBannerMessage: "",
    icon: "",
    showSuggestEdit: false,
  },
);

const emit = defineEmits(["save", "open-save-modal", "open-cancel-modal"]);

interface KeyLabelPair {
  key: string;
  label: string;
  tooltip?: string;
  emptyValueBehavior?: { action: string };
}

const resultDataForDisplay = computed(
  () => props.data as Record<string, unknown>,
);

const computedKeyLabelPairs = computed(() => {
  if (props.labels && Object.keys(props.labels).length > 0) {
    const tooltips = props.tooltips as Record<string, string> | undefined;
    return Object.entries(props.labels).map(([key, label]) => ({
      key,
      label,
      tooltip: tooltips?.[key],
      emptyValueBehavior: { action: "hide" },
    }));
  }
  return props.keyLabelPairs ?? [];
});

const keyLabelPairsForDisplay = computed(
  () => computedKeyLabelPairs.value as KeyLabelPair[],
);
</script>
