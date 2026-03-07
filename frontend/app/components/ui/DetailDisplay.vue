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
          >
            <template
              v-for="(_, name) in $slots"
              :key="name"
              #[name]="slotData"
            >
              <slot :name="name" v-bind="slotData" />
            </template>
          </BaseCardHeader>
        </template>

        <slot name="full-width" />

        <div class="gradient-top-border" />

        <div class="flex">
          <div
            class="main-content flex w-full flex-col gap-2 px-4 py-4 sm:px-6 sm:py-6"
          >
            <slot />
            <template v-for="(item, index) in keyLabelPairs" :key="index">
              <section
                v-if="shouldDisplayValue(item, resultData?.[item.key])"
                class="detail-section"
              >
                <template v-if="item.key === 'Region'">
                  <slot />
                </template>
                <template
                  v-if="$slots[item.key.replace(/ /g, '-').toLowerCase()]"
                >
                  <slot
                    :name="item.key.replace(/ /g, '-').toLowerCase()"
                    :value="resultData?.[item.key]"
                  />
                </template>
                <template v-else>
                  <DetailRow :label="item.label" :tooltip="item.tooltip">
                    <template #label-actions>
                      <slot
                        :name="item.key + '-header-actions'"
                        :value="resultData?.[item.key]"
                      />
                    </template>

                    <template
                      v-if="
                        (item.key === 'Answer' || item.key === 'Specialists') &&
                        Array.isArray(
                          getDisplayValue(item, resultData?.[item.key]),
                        )
                      "
                    >
                      <div class="mt-0 flex flex-col gap-2">
                        <div
                          v-for="(line, i) in getDisplayValue(
                            item,
                            resultData?.[item.key],
                          ) as string[]"
                          :key="i"
                          :class="
                            props.valueClassMap[item.key] ||
                            'result-value-small'
                          "
                        >
                          {{ line }}
                        </div>
                      </div>
                    </template>
                    <template v-else>
                      <p
                        :class="[
                          props.valueClassMap[item.key] ||
                            'result-value-small whitespace-pre-line',
                          'mt-0',
                        ]"
                      >
                        {{ getDisplayValue(item, resultData?.[item.key]) }}
                      </p>
                    </template>
                  </DetailRow>
                </template>
              </section>
            </template>
            <slot name="search-links" />
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
import { useSlots, computed } from "vue";
import { useRoute } from "vue-router";
import { useCoveredCountries } from "@/composables/useJurisdictions";
import BaseCardHeader from "@/components/ui/CardHeader.vue";
import ContributeBanner from "@/components/ui/ContributeBanner.vue";
import NotificationBanner from "@/components/ui/NotificationBanner.vue";
import LoadingCard from "@/components/layout/LoadingCard.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import InlineError from "@/components/ui/InlineError.vue";

interface EmptyValueBehavior {
  action?: string;
  fallback?: string;
  getFallback?: (data: Record<string, unknown>) => string;
  shouldDisplay?: (data: Record<string, unknown>) => boolean;
  shouldHide?: (data: Record<string, unknown>) => boolean;
}

interface KeyLabelPair {
  key: string;
  label: string;
  tooltip?: string;
  emptyValueBehavior?: EmptyValueBehavior;
  valueTransform?: (value: unknown) => unknown;
}

interface Props {
  loading: boolean;
  error?: Error | Record<string, unknown> | null;
  resultData: Record<string, unknown>;
  keyLabelPairs: KeyLabelPair[];
  valueClassMap: Record<string, string>;
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
  keyLabelPairs: () => [],
  valueClassMap: () => ({}),
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
      ? route.params.id
      : isQuestionPage
        ? newData.JurisdictionCode
        : null;

    jurisdictionCode.value =
      typeof rawJurisdiction === "string"
        ? rawJurisdiction.toLowerCase()
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
    !!(props.resultData?.Name || props.resultData?.["Jurisdictions"])
  );
});

const contributeBannerJurisdictionName = computed((): string => {
  return (
    (props.resultData?.Name as string) ||
    (props.resultData?.["Jurisdictions"] as string) ||
    ""
  );
});

const slots = useSlots();

const selfFetchingSlots = new Set([
  "oup-chapter",
  "related-literature",
  "literature",
]);

function shouldDisplayValue(item: KeyLabelPair, value: unknown): boolean {
  const slotName = item.key.replace(/ /g, "-").toLowerCase();

  if (slots[slotName] && selfFetchingSlots.has(slotName)) return true;

  if (!item.emptyValueBehavior) return true;
  if (
    item.emptyValueBehavior.shouldDisplay &&
    !item.emptyValueBehavior.shouldDisplay(props.resultData)
  ) {
    return false;
  }
  if (
    item.emptyValueBehavior.shouldHide &&
    item.emptyValueBehavior.shouldHide(props.resultData)
  ) {
    return false;
  }
  if (
    item.emptyValueBehavior.action === "hide" &&
    (!value || value === "NA" || value === "N/A")
  ) {
    return false;
  }
  return true;
}

function getDisplayValue(item: KeyLabelPair, value: unknown): unknown {
  if (item.valueTransform) {
    return item.valueTransform(value);
  }
  if (
    (item.key === "Answer" || item.key === "Specialists") &&
    typeof value === "string" &&
    value.includes(",")
  ) {
    return value.split(",").map((part) => part.trim());
  }
  if (
    Array.isArray(value) &&
    value.length === 0 &&
    item.emptyValueBehavior &&
    item.emptyValueBehavior.action === "display"
  ) {
    return "—";
  }
  if (!item.emptyValueBehavior) return value || "—";
  if (
    (!value || value === "NA") &&
    item.emptyValueBehavior.action === "display"
  ) {
    if (item.emptyValueBehavior.getFallback) {
      return item.emptyValueBehavior.getFallback(props.resultData);
    }
    return "—";
  }
  return value;
}
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
