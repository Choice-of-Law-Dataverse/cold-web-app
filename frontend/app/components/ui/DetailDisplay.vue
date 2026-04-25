<template>
  <article>
    <NotificationBanner
      v-if="showNotificationBanner"
      :notification-banner-message="notificationBannerMessage"
      :icon="icon"
    />

    <LoadingCard v-if="loading" />
    <InlineError v-else-if="error" :error="error" />
    <template v-else>
      <UCard
        :ui="{
          body: '!p-0',
          header: 'sticky-header border-b-0 px-6 py-5',
        }"
      >
        <template v-if="showHeader" #header>
          <div class="detail-header">
            <div class="detail-header__title-block">
              <component
                :is="titleTag"
                v-if="hasTitle"
                class="detail-header__title"
              >
                <slot name="title">{{ resolvedTitle }}</slot>
              </component>
              <div v-if="hasCaption" class="detail-header__caption">
                <slot name="title-caption">{{ resolvedCaption }}</slot>
              </div>
            </div>
            <div v-if="$slots['title-actions']" class="detail-header__actions">
              <slot name="title-actions" />
            </div>
          </div>
        </template>

        <slot name="full-width" />

        <div class="gradient-top-border" />

        <MetaBand
          v-if="showHeader"
          :result-data="resultData"
          :card-type="formattedSourceTable"
          :formatted-jurisdiction="formattedJurisdiction"
          :formatted-theme="formattedTheme"
          :legal-family="legalFamily"
          :header-mode="headerMode"
          :show-cite="showCite"
          :show-json="showJson"
          :show-print="showPrint"
          :show-legal-family="showLegalFamily"
          @open-save-modal="emit('open-save-modal')"
        />

        <div class="flex">
          <div
            class="main-content flex w-full flex-col gap-2 px-4 py-4 sm:px-6 sm:py-6"
          >
            <slot />
          </div>
        </div>
        <ContributeBanner
          v-if="shouldShowContributeBanner"
          :jurisdiction-name="contributeBannerJurisdictionName"
        />
        <slot name="footer" />
      </UCard>
    </template>
  </article>
</template>

<script setup lang="ts">
import { computed, ref, useSlots, watch, watchEffect } from "vue";
import { useRoute } from "vue-router";
import { useCoveredCountries } from "@/composables/useJurisdictions";
import { getEntityConfig } from "@/config/entityRegistry";
import MetaBand from "@/components/ui/MetaBand.vue";
import ContributeBanner from "@/components/ui/ContributeBanner.vue";
import NotificationBanner from "@/components/ui/NotificationBanner.vue";
import LoadingCard from "@/components/layout/LoadingCard.vue";
import InlineError from "@/components/ui/InlineError.vue";

interface Props {
  loading: boolean;
  error?: Error | Record<string, unknown> | null;
  resultData: Record<string, unknown>;
  basePath?: string;
  formattedSourceTable: string;
  showHeader: boolean;
  showCite?: boolean;
  showJson?: boolean;
  showPrint?: boolean;
  showLegalFamily?: boolean;
  formattedJurisdiction: string[];
  formattedTheme: string[];
  legalFamily?: string[];
  headerMode: string;
  showNotificationBanner: boolean;
  notificationBannerMessage: string;
  icon: string;
  titleTag?: string;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  error: null,
  resultData: () => ({}),
  basePath: "",
  formattedSourceTable: "",
  showHeader: true,
  showCite: true,
  showJson: true,
  showPrint: true,
  showLegalFamily: true,
  formattedJurisdiction: () => [],
  formattedTheme: () => [],
  legalFamily: () => [],
  headerMode: "default",
  showNotificationBanner: false,
  notificationBannerMessage: "",
  icon: "",
  titleTag: "h1",
});

const emit = defineEmits<{
  save: [];
  "open-save-modal": [];
  "open-cancel-modal": [];
}>();

const slots = useSlots();

const formattedSourceTable = computed(
  () =>
    props.formattedSourceTable || String(props.resultData?.sourceTable ?? ""),
);

const entityConfig = computed(() =>
  props.basePath ? getEntityConfig(props.basePath) : undefined,
);

const resolvedTitle = computed(() => {
  if (props.headerMode === "new") return "";
  const titleKey = entityConfig.value?.titleKey;
  if (!titleKey) return "";
  const value = (props.resultData as Record<string, unknown>)[titleKey];
  return typeof value === "string" ? value : "";
});

const hasTitle = computed(() => {
  if (slots.title) return true;
  return resolvedTitle.value.trim().length > 0;
});

const resolvedCaption = computed(() => "");
const hasCaption = computed(() => !!slots["title-caption"]);

const route = useRoute();
const isJurisdictionPage = route.path.startsWith("/jurisdiction/");
const isQuestionPage = route.path.startsWith("/question/");
const jurisdictionCode = ref<string | null>(null);
const { data: coveredCountriesSet } = useCoveredCountries();
const shouldShowBanner = ref(false);

watch(
  () => props.resultData,
  (newData: Record<string, unknown>) => {
    if (!newData) return;
    const rawJurisdiction = isJurisdictionPage
      ? route.params.coldId
      : isQuestionPage
        ? newData.jurisdictionCode
        : null;
    jurisdictionCode.value =
      typeof rawJurisdiction === "string"
        ? rawJurisdiction.toUpperCase()
        : null;
  },
  { immediate: true },
);

watchEffect(() => {
  if (
    (isJurisdictionPage || isQuestionPage) &&
    jurisdictionCode.value &&
    coveredCountriesSet.value
  ) {
    shouldShowBanner.value = !coveredCountriesSet.value.has(
      jurisdictionCode.value,
    );
  }
});

const shouldShowContributeBanner = computed(
  () =>
    shouldShowBanner.value &&
    !!(props.resultData?.name || props.resultData?.jurisdictions),
);

const contributeBannerJurisdictionName = computed(
  () =>
    (props.resultData?.name as string) ||
    (props.resultData?.jurisdictions as string) ||
    "",
);
</script>

<style scoped>
:deep(.sticky-header) {
  z-index: 10;
  background-color: white;
}

:deep(.dark .sticky-header) {
  background-color: rgb(17 24 39);
}

.detail-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 16px;
  align-items: start;
}

.detail-header__title-block {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-bottom: 4px;
}

.detail-header__title {
  font-family: "DM Sans", sans-serif;
  font-weight: 500;
  font-size: clamp(20px, 2.2vw, 24px);
  line-height: 1.3;
  letter-spacing: -0.015em;
  margin: 0;
  color: var(--color-cold-night);
  overflow-wrap: break-word;
}

.detail-header__caption {
  font-family: "IBM Plex Mono", monospace;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-cold-night-alpha);
}

.detail-header__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 4px;
  flex-shrink: 0;
}
</style>
