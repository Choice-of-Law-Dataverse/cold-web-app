<template>
  <main class="px-6">
    <div class="mx-auto w-full max-w-container">
      <div class="col-span-12">
        <DetailDisplay
          :loading="loading"
          :result-data="resultData"
          :key-label-pairs="keyLabelPairs"
          :value-class-map="valueClassMap"
          :formatted-source-table="sourceTable"
          :formatted-jurisdiction="formattedJurisdiction"
          :show-header="showHeader"
          :show-open-link="showOpenLink"
          :show-suggest-edit="showSuggestEdit"
          :formatted-theme="formattedTheme"
          :hide-back-button="hideBackButton"
          :header-mode="headerMode"
          :show-notification-banner="showNotificationBanner"
          :notification-banner-message="notificationBannerMessage"
          :fallback-message="fallbackMessage"
          :icon="icon"
          @save="$emit('save')"
          @open-save-modal="$emit('open-save-modal')"
          @open-cancel-modal="$emit('open-cancel-modal')"
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

const _props = withDefaults(
  defineProps<{
    loading: boolean;
    resultData: any;
    keyLabelPairs: any[];
    valueClassMap: Record<string, string>;
    sourceTable: string;
    formattedJurisdiction?: any[]; //
    hideBackButton?: boolean;
    showHeader?: boolean;
    formattedTheme?: any[];
    headerMode?: string;
    showNotificationBanner?: boolean;
    notificationBannerMessage?: string;
    fallbackMessage?: string;
    icon?: string;
    showOpenLink?: boolean;
    showSuggestEdit?: boolean;
  }>(),
  {
    showHeader: true,
    showOpenLink: false,
    showSuggestEdit: false,
  },
);

defineEmits(["save", "open-save-modal", "open-cancel-modal"]);
</script>
