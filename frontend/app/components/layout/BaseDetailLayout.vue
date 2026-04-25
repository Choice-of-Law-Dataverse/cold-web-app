<template>
  <DetailDisplay
    :loading="props.loading"
    :error="props.error ?? undefined"
    :result-data="resultDataForDisplay"
    :base-path="basePath"
    :formatted-source-table="props.table"
    :formatted-jurisdiction="props.formattedJurisdiction"
    :formatted-theme="props.formattedTheme"
    :legal-family="props.legalFamily"
    :show-header="true"
    :show-cite="props.showCite"
    :show-json="props.showJson"
    :show-print="props.showPrint"
    :show-legal-family="props.showLegalFamily"
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

<script setup lang="ts">
import { computed } from "vue";
import DetailDisplay from "@/components/ui/DetailDisplay.vue";
import {
  getBasePathForTable,
  type ProcessedEntity,
} from "@/config/entityRegistry";

const props = withDefaults(
  defineProps<{
    table: string;
    loading: boolean;
    error?: Error | null;
    data: ProcessedEntity | null;
    formattedJurisdiction?: string[];
    formattedTheme?: string[];
    legalFamily?: string[];
    headerMode?: string;
    showNotificationBanner?: boolean;
    notificationBannerMessage?: string;
    icon?: string;
    showSuggestEdit?: boolean;
    showCite?: boolean;
    showJson?: boolean;
    showPrint?: boolean;
    showLegalFamily?: boolean;
  }>(),
  {
    error: undefined,
    data: null,
    formattedJurisdiction: () => [],
    formattedTheme: () => [],
    legalFamily: () => [],
    headerMode: "default",
    showNotificationBanner: false,
    notificationBannerMessage: "",
    icon: "",
    showSuggestEdit: false,
    showCite: true,
    showJson: true,
    showPrint: true,
    showLegalFamily: true,
  },
);

const emit = defineEmits(["save", "open-save-modal", "open-cancel-modal"]);

const resultDataForDisplay = computed(
  () => (props.data ?? {}) as Record<string, unknown>,
);

const basePath = computed(() => getBasePathForTable(props.table) ?? "");
</script>
