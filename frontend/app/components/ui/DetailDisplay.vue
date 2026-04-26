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
          header: 'sticky-header border-b-0 !p-0',
        }"
      >
        <template v-if="showHeader" #header>
          <MetaBand
            :result-data="resultData"
            :card-type="formattedSourceTable"
            :formatted-jurisdiction="formattedJurisdiction"
            :formatted-theme="formattedTheme"
            :header-mode="headerMode"
            :show-cite="showCite"
            :show-json="showJson"
            :show-print="showPrint"
            :entity-type="entityType"
            :entity-id="entityId"
            :entity-title="entityTitle"
            @open-save-modal="emit('open-save-modal')"
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
        <div v-if="formattedUpdatedAt" class="footer-band">
          <span class="footer-band__label">Updated</span>
          <time :datetime="updatedAtIso">{{ formattedUpdatedAt }}</time>
        </div>
      </UCard>
    </template>
  </article>
</template>

<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";
import { useRoute } from "vue-router";
import { useCoveredCountries } from "@/composables/useJurisdictions";
import { formatDate } from "@/utils/format";
import MetaBand from "@/components/ui/MetaBand.vue";
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
  showCite?: boolean;
  showJson?: boolean;
  showPrint?: boolean;
  formattedJurisdiction: string[];
  formattedTheme: string[];
  headerMode: string;
  showNotificationBanner: boolean;
  notificationBannerMessage: string;
  icon: string;
  entityType?: string;
  entityId?: string;
  entityTitle?: string;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  error: null,
  resultData: () => ({}),
  formattedSourceTable: "",
  showHeader: true,
  showCite: true,
  showJson: true,
  showPrint: true,
  formattedJurisdiction: () => [],
  formattedTheme: () => [],
  headerMode: "default",
  showNotificationBanner: false,
  notificationBannerMessage: "",
  icon: "",
  entityType: "",
  entityId: "",
  entityTitle: "",
});

const emit = defineEmits<{
  save: [];
  "open-save-modal": [];
  "open-cancel-modal": [];
}>();

const formattedSourceTable = computed(
  () =>
    props.formattedSourceTable || String(props.resultData?.sourceTable ?? ""),
);

const updatedAtIso = computed(() => {
  const value = props.resultData?.updatedAt;
  return typeof value === "string" ? value : "";
});

const formattedUpdatedAt = computed(() => {
  if (!updatedAtIso.value) return "";
  return formatDate(updatedAtIso.value) ?? updatedAtIso.value;
});

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

.footer-band {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 0.5rem 1.5rem;
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-purple) 3%, white),
    color-mix(in srgb, var(--color-cold-green) 2%, white)
  );
  border-top: 1px solid
    color-mix(in srgb, var(--color-cold-gray) 70%, transparent);
  font-family: "IBM Plex Mono", monospace;
  font-size: 11px;
  color: var(--color-cold-night-alpha);
}

.footer-band__label {
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-cold-night-alpha-25);
}

.footer-band time {
  color: var(--color-cold-night-alpha);
  font-feature-settings: "tnum";
}
</style>
