<template>
  <DetailDisplay
    :loading="props.loading"
    :error="props.error ?? undefined"
    :result-data="resultDataForDisplay"
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

<script setup lang="ts">
import { computed } from "vue";
import DetailDisplay from "@/components/ui/DetailDisplay.vue";
import type { ProcessedEntity } from "@/config/entityRegistry";

const props = withDefaults(
  defineProps<{
    table: string;
    loading: boolean;
    error?: Error | null;
    data: ProcessedEntity | null;
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
    data: null,
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

const resultDataForDisplay = computed(
  () => (props.data ?? {}) as Record<string, unknown>,
);
</script>
