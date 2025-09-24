<template>
  <main class="px-6">
    <div class="mx-auto w-full max-w-container">
      <div class="col-span-12">
        <DetailDisplay
          :loading="props.loading"
          :result-data="props.resultData"
          :key-label-pairs="props.keyLabelPairs"
          :value-class-map="props.valueClassMap"
          :formatted-source-table="props.sourceTable"
          :formatted-jurisdiction="props.formattedJurisdiction"
          :show-header="props.showHeader"
          :show-open-link="props.showOpenLink"
          :show-suggest-edit="props.showSuggestEdit"
          :formatted-theme="props.formattedTheme"
          :hide-back-button="props.hideBackButton"
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
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import DetailDisplay from "@/components/ui/BaseDetailDisplay.vue";

const props = withDefaults(
  defineProps<{
    loading: boolean;
    resultData: Record<string, unknown>;
    keyLabelPairs: Record<string, unknown>[];
    valueClassMap: Record<string, string>;
    sourceTable: string;
    formattedJurisdiction?: Record<string, unknown>[];
    hideBackButton?: boolean;
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
</script>
