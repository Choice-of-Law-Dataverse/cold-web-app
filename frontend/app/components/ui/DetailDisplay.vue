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
          <BaseCardHeader
            :result-data="resultData"
            :card-type="formattedSourceTable"
            :show-suggest-edit="showSuggestEdit"
            :show-open-link="showOpenLink"
            :formatted-jurisdiction="formattedJurisdiction"
            :formatted-theme="formattedTheme"
            :header-mode="headerMode"
            @save="emit('save')"
            @open-save-modal="emit('open-save-modal')"
            @open-cancel-modal="emit('open-cancel-modal')"
          />
        </template>

        <slot name="full-width" />

        <div class="gradient-top-border" />

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
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useCoveredCountries } from "@/composables/useJurisdictions";
import BaseCardHeader from "@/components/ui/CardHeader.vue";
import ContributeBanner from "@/components/ui/ContributeBanner.vue";
import NotificationBanner from "@/components/ui/NotificationBanner.vue";
import LoadingCard from "@/components/layout/LoadingCard.vue";
import InlineError from "@/components/ui/InlineError.vue";

interface Props {
  loading: boolean;
  error?: Error | Record<string, unknown> | null;
  resultData: Record<string, unknown>;
  formattedSourceTable: string;
  showHeader: boolean;
  showOpenLink: boolean;
  showSuggestEdit: boolean;
  formattedJurisdiction: string[];
  formattedTheme: string[];
  headerMode: string;
  showNotificationBanner: boolean;
  notificationBannerMessage: string;
  icon: string;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  error: null,
  resultData: () => ({}),
  formattedSourceTable: "",
  showHeader: true,
  showOpenLink: false,
  showSuggestEdit: false,
  formattedJurisdiction: () => [],
  formattedTheme: () => [],
  headerMode: "default",
  showNotificationBanner: false,
  notificationBannerMessage: "",
  icon: "",
});

const emit = defineEmits<{
  save: [];
  "open-save-modal": [];
  "open-cancel-modal": [];
}>();

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

const shouldShowContributeBanner = computed((): boolean => {
  return (
    shouldShowBanner.value &&
    !!(props.resultData?.name || props.resultData?.jurisdictions)
  );
});

const contributeBannerJurisdictionName = computed((): string => {
  return (
    (props.resultData?.name as string) ||
    (props.resultData?.jurisdictions as string) ||
    ""
  );
});
</script>

<style scoped>
.label-key {
  padding: 0;
}

.label-key span {
  display: inline-flex;
  align-items: center;
}

.label-key span :deep(svg) {
  margin-top: -1px;
  color: var(--color-cold-purple);
  font-size: 1.1em;
}

:deep(.sticky-header) {
  z-index: 10;
  background-color: white;
}

:deep(.dark .sticky-header) {
  background-color: rgb(17 24 39);
}
</style>
