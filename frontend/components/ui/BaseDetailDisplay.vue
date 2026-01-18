<template>
  <NotificationBanner
    v-if="showNotificationBanner"
    :notification-banner-message="notificationBannerMessage"
    :fallback-message="fallbackMessage"
    :icon="icon"
  />

  <NotificationBanner
    v-else-if="
      shouldShowBanner &&
      (props.resultData?.Name || props.resultData?.['Jurisdictions'])
    "
    :jurisdiction-name="
      props.resultData?.Name || props.resultData?.['Jurisdictions']
    "
    :fallback-message="fallbackMessage"
    :icon="icon"
  />

  <template v-if="loading">
    <LoadingCard />
  </template>
  <template v-else>
    <UCard
      class="cold-ucard"
      :ui="{
        base: 'overflow-hidden',
        body: {
          base: '',
          padding: '',
        },
        header: {
          base: 'sticky-header border-bottom-0',
          padding: 'px-6 py-5',
        },
      }"
    >
      <!-- Header section: render only when showHeader is true -->
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
          <template v-for="(_, name) in $slots" :key="name" #[name]="slotData">
            <slot :name="name" v-bind="slotData" />
          </template>
        </BaseCardHeader>
      </template>

      <slot name="full-width" />

      <!-- Main content -->
      <div class="gradient-top-border flex">
        <div
          class="main-content flex w-full flex-col gap-2 px-6 py-6 sm:px-8 sm:py-8"
        >
          <!-- Render custom slot content (e.g., form fields) before keyLabelPairs -->
          <slot />
          <!-- Loop over keyLabelPairs to display each key-value pair dynamically -->
          <template v-for="(item, index) in keyLabelPairs" :key="index">
            <section
              v-if="shouldDisplayValue(item, resultData?.[item.key])"
              class="detail-section"
            >
              <!-- Check if it's the special 'Specialist' key -->
              <template v-if="item.key === 'Region'">
                <slot />
              </template>
              <!-- Check for slot first -->
              <template
                v-if="$slots[item.key.replace(/ /g, '-').toLowerCase()]"
              >
                <slot
                  :name="item.key.replace(/ /g, '-').toLowerCase()"
                  :value="resultData?.[item.key]"
                />
              </template>
              <!-- If no slot, use default display -->
              <template v-else>
                <!-- Conditionally render the label and value container -->
                <DetailRow :label="item.label" :tooltip="item.tooltip">
                  <template #label-actions>
                    <slot
                      :name="item.key + '-header-actions'"
                      :value="resultData?.[item.key]"
                    />
                  </template>

                  <!-- Conditionally render bullet list if Answer or Specialists is an array -->
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
                        )"
                        :key="i"
                        :class="
                          props.valueClassMap[item.key] || 'result-value-small'
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
      <!-- Footer slot for full-width content like country report banner -->
      <slot name="footer" />
    </UCard>
  </template>
</template>

<script setup>
import { useSlots } from "vue";
import { useRoute } from "vue-router";
import { useCoveredCountries } from "@/composables/useJurisdictions";
import BaseCardHeader from "@/components/ui/BaseCardHeader.vue";
import NotificationBanner from "@/components/ui/NotificationBanner.vue";
import LoadingCard from "@/components/layout/LoadingCard.vue";
import DetailRow from "@/components/ui/DetailRow.vue";

const props = defineProps({
  loading: Boolean,
  resultData: {
    type: Object,
    default: () => ({}),
  },
  keyLabelPairs: {
    type: Array,
    default: () => [],
  },
  valueClassMap: {
    type: Object,
    default: () => ({}),
  },
  formattedSourceTable: {
    type: String,
    default: "",
  },
  showHeader: {
    type: Boolean,
    default: true,
  },
  showOpenLink: {
    type: Boolean,
    default: false,
  },
  showSuggestEdit: {
    type: Boolean,
    default: false,
  },
  formattedJurisdiction: { type: Array, required: false, default: () => [] },
  formattedTheme: { type: Array, required: false, default: () => [] },
  headerMode: {
    type: String,
    default: "default",
  },
  showNotificationBanner: Boolean,
  notificationBannerMessage: {
    type: String,
    default: "",
  },
  fallbackMessage: {
    type: String,
    default: "",
  },
  icon: {
    type: String,
    required: false,
    default: "",
  },
});

const emit = defineEmits(["save", "open-save-modal", "open-cancel-modal"]);

const route = useRoute();
const isJurisdictionPage = route.path.startsWith("/jurisdiction/");
const isQuestionPage = route.path.startsWith("/question/");
const jurisdictionCode = ref(null);
const { data: coveredCountriesSet } = useCoveredCountries();
const shouldShowBanner = ref(false);

watch(
  () => props.resultData,
  (newData) => {
    if (!newData) return;

    const rawJurisdiction = isJurisdictionPage
      ? route.params.id
      : isQuestionPage
        ? newData["Jurisdictions Alpha-3 Code"] || newData.JurisdictionCode
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

const slots = useSlots();

const shouldDisplayValue = (item, value) => {
  // Always show if a custom slot exists for this field (slot handles its own data)
  const slotName = item.key.replace(/ /g, "-").toLowerCase();
  if (slots[slotName]) return true;

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
};

const getDisplayValue = (item, value) => {
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
};
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
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: white;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}

:deep(.dark .sticky-header) {
  background-color: rgb(17 24 39);
}
</style>
