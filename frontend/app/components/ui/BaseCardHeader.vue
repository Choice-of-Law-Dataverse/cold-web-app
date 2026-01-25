<template>
  <div
    :key="formattedJurisdiction + formattedTheme + legalFamily"
    class="header-container flex flex-wrap items-center justify-between gap-3"
  >
    <template v-if="cardType === 'Loading'" />
    <template v-else>
      <!-- Mobile: Actions menu (outside tags container to stay top-right) -->
      <div
        v-if="showSuggestEdit && headerMode !== 'new'"
        class="order-last sm:hidden"
      >
        <UDropdownMenu :items="mobileMenuItems">
          <UButton
            icon="i-material-symbols:more-vert"
            variant="ghost"
            color="neutral"
            size="sm"
          />
        </UDropdownMenu>
      </div>

      <!-- Left side of the header: Tags -->
      <div
        class="tags-container scrollbar-hidden flex flex-1 flex-wrap items-center gap-2.5 overflow-x-auto"
      >
        <!-- Display 'Name (from Jurisdiction)' or alternatives -->
        <NuxtLink
          v-for="(jurisdictionString, index) in formattedJurisdiction"
          :key="`jurisdiction-${index}`"
          class="label-jurisdiction label-link jurisdiction-label-link cursor-pointer"
          :to="`/search?jurisdiction=${encodeURIComponent(jurisdictionString).replace(/%20/g, '+')}`"
        >
          <span class="hover-flag">
            <img
              :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${getJurisdictionISO(jurisdictionString)}.svg`"
              class="flag-icon"
            />
          </span>
          {{ jurisdictionString }}
        </NuxtLink>
        <!-- Legal Family next to jurisdiction name -->
        <span
          v-for="(family, index) in legalFamily"
          :key="`legal-family-${index}`"
          class="label-theme"
        >
          {{ family }}
        </span>
        <!-- Display 'source_table' or a type selector when in 'new' mode -->
        <template v-if="adjustedSourceTable">
          <!-- In 'new' mode, show the data type label style and a link to reveal the dropdown -->
          <div v-if="headerMode === 'new'" class="flex items-center">
            <span :class="['label', labelColorClass, '']">
              {{ adjustedSourceTable }}
            </span>
            <div class="-ml-2">
              <USelect
                v-model="selectedType"
                variant="none"
                placeholder=" "
                :items="typeOptions"
                value-key="value"
                label-key="label"
                :class="[
                  'no-caret-select',
                  'leading-none',
                  'new-select-label',
                  '!text-[var(--color-cold-purple)]',
                ]"
              >
                <!-- Custom caret (replaces default chevron) -->
                <template #trailing>
                  <span class="custom-caret" aria-hidden="true">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      width="16"
                      height="16"
                      fill="none"
                      class="rotate-90 text-white"
                    >
                      <path
                        d="M9 6l6 6-6 6"
                        stroke="currentColor"
                        stroke-width="3"
                        stroke-linecap="square"
                        stroke-linejoin="square"
                      />
                    </svg>
                  </span>
                </template>
              </USelect>
            </div>
          </div>
          <!-- In other modes, keep the clickable label linking to search -->
          <template v-else>
            <!-- Remove link functionality for Arbitral Rule, Arbitral Award, and Jurisdiction -->
            <span
              v-if="
                ['Arbitral Rule', 'Arbitral Award', 'Jurisdiction'].includes(
                  adjustedSourceTable,
                )
              "
              :class="['label', labelColorClass, '']"
            >
              {{ adjustedSourceTable }}
            </span>
            <NuxtLink
              v-else
              :to="
                '/search?type=' +
                encodeURIComponent(
                  getSourceTablePlural(adjustedSourceTable),
                ).replace(/%20/g, '+')
              "
              :class="[
                'label',
                labelColorClass,
                'label-link',
                'cursor-pointer',
              ]"
            >
              {{ adjustedSourceTable }}
            </NuxtLink>
          </template>
        </template>

        <!-- Display 'Themes' -->
        <NuxtLink
          v-for="(theme, index) in formattedTheme"
          :key="`theme-${index}`"
          class="label-theme label-link cursor-pointer"
          :to="
            '/search?theme=' + encodeURIComponent(theme).replace(/%20/g, '+')
          "
        >
          {{ theme }}
        </NuxtLink>

        <div class="ml-auto flex items-center justify-self-end">
          <template v-if="headerMode === 'new'">
            <UButton
              size="xs"
              class="bg-cold-purple hover:bg-cold-purple/90 text-white"
              @click="emit('open-save-modal')"
            >
              Submit your data
            </UButton>
          </template>
          <template v-else>
            <template v-if="showSuggestEdit">
              <!-- Desktop: Inline actions -->
              <div
                class="actions-container hidden flex-row items-center gap-1.5 sm:flex"
              >
                <!-- All actions except the International Instrument Edit link -->
                <template
                  v-for="(action, index) in suggestEditActions.filter(
                    (a) =>
                      !(
                        props.cardType === 'International Instrument' &&
                        a.label === 'Edit'
                      ),
                  )"
                  :key="index"
                >
                  <button
                    v-if="action.label === 'Cite'"
                    type="button"
                    class="action-button"
                    @click.prevent="isCiteOpen = true"
                  >
                    <UIcon
                      :name="action.icon"
                      class="inline-block text-[1.2em]"
                    />
                    {{ action.label }}
                  </button>
                  <button
                    v-else-if="action.label === 'JSON'"
                    type="button"
                    class="action-button"
                    @click.prevent="exportJSON"
                  >
                    <UIcon
                      :name="action.icon"
                      class="inline-block text-[1.2em]"
                    />
                    {{ action.label }}
                  </button>
                  <button
                    v-else-if="action.label === 'Print'"
                    type="button"
                    class="action-button"
                    @click.prevent="printPage"
                  >
                    <UIcon
                      :name="action.icon"
                      class="inline-block text-[1.2em]"
                    />
                    {{ action.label }}
                  </button>
                  <NuxtLink
                    v-else
                    class="action-button"
                    :class="action.class"
                    v-bind="action.to ? { to: action.to } : {}"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <UIcon
                      :name="action.icon"
                      class="inline-block text-[1.2em]"
                    />
                    {{ action.label }}
                  </NuxtLink>
                </template>
                <!-- The Edit link for International Instrument only, no target/rel -->
                <NuxtLink
                  v-for="(action, index) in suggestEditActions.filter(
                    (a) =>
                      props.cardType === 'International Instrument' &&
                      a.label === 'Edit',
                  )"
                  :key="'edit-' + index"
                  class="action-button"
                  :class="action.class"
                  v-bind="action.to ? { to: action.to } : {}"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <UIcon
                    :name="action.icon"
                    class="inline-block text-[1.2em]"
                  />
                  {{ action.label }}
                </NuxtLink>
              </div>
            </template>
            <template v-else-if="showOpenLink">
              <div class="arrow-container">
                <UIcon
                  name="i-material-symbols:arrow-forward"
                  class="arrow-icon"
                />
              </div>
            </template>
          </template>
        </div>
      </div>
    </template>
  </div>
  <CiteModal v-model="isCiteOpen" />
</template>

<script setup>
import { onMounted, ref, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { parseJurisdictionString } from "@/utils/jurisdictionParser";
import { useJurisdictionLookup } from "@/composables/useJurisdictions";
import CiteModal from "@/components/ui/CiteModal.vue";

const emit = defineEmits(["save", "open-save-modal", "open-cancel-modal"]);

const route = useRoute();
const router = useRouter();
const isCiteOpen = ref(false);

const { getJurisdictionISO } = useJurisdictionLookup();

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
  cardType: {
    type: String,
    required: true,
  },
  showSuggestEdit: {
    type: Boolean,
    default: true,
  },
  showOpenLink: {
    type: Boolean,
    default: true,
  },
  formattedJurisdiction: {
    type: Array,
    required: false,
    default: () => [],
  },
  formattedTheme: {
    type: Array,
    required: false,
    default: () => [],
  },
  headerMode: {
    type: String,
    default: "default",
  },
});

const formattedJurisdiction = computed(() => {
  if (props.formattedJurisdiction.length > 0) {
    return props.formattedJurisdiction;
  }
  const jurisdictionString =
    props.resultData["Jurisdiction name"] ||
    props.resultData["Jurisdiction Names"] ||
    props.resultData["Name (from Jurisdiction)"] ||
    props.resultData["Jurisdiction"] ||
    props.resultData["Jurisdictions"] ||
    props.resultData["Instrument"] ||
    "";

  if (!jurisdictionString) {
    return [];
  }

  return parseJurisdictionString(jurisdictionString);
});

const formattedSourceTable = computed(() => {
  return props.cardType || props.resultData?.source_table || "";
});

const adjustedSourceTable = computed(() => {
  switch (formattedSourceTable.value) {
    case "Court Decisions":
      return "Court Decision";
    case "Answers":
      return "Question";
    case "Domestic Instrument":
      return "Domestic Instrument";
    case "Regional Instrument":
      return "Regional Instrument";
    case "International Instrument":
      return "International Instrument";
    case "Literature":
      return "Literature";
    case "Arbitral Rule":
      return "Arbitral Rule";
    case "Arbitral Award":
      return "Arbitral Award";
    case "Jurisdiction":
      return "Jurisdiction";
    default:
      return formattedSourceTable.value || "";
  }
});

const labelColorClass = computed(() => {
  switch (formattedSourceTable.value) {
    case "Court Decisions":
    case "Court Decision":
      return "label-court-decision";
    case "Answers":
    case "Question":
      return "label-question";
    case "Domestic Instrument":
    case "Regional Instrument":
    case "International Instrument":
      return "label-instrument";
    case "Arbitral Rule":
    case "Arbitral Award":
      return "label-arbitration";
    case "Literature":
      return "label-literature";
    case "Jurisdiction":
      return "hidden";
    default:
      return "";
  }
});

const formattedTheme = computed(() => {
  if (props.formattedTheme.length > 0) {
    return props.formattedTheme;
  }

  if (props.cardType === "Literature" && props.resultData["Themes"]) {
    return props.resultData["Themes"].split(",").map((theme) => theme.trim());
  }

  const themes =
    props.resultData["Title of the Provision"] ?? props.resultData.Themes;

  if (!themes || themes === "None") {
    return [];
  }

  return [...new Set(themes.split(",").map((theme) => theme.trim()))];
});

const suggestEditActions = computed(() => {
  const actions = [];

  actions.push({
    label: "Cite",
    icon: "i-material-symbols:verified-outline",
  });

  // Add JSON export button
  actions.push({
    label: "JSON",
    icon: "i-material-symbols:data-object",
  });

  // Add Print button
  actions.push({
    label: "Print",
    icon: "i-material-symbols:print-outline",
  });

  const editLink = suggestEditLink.value;
  actions.push({
    label: "Edit",
    icon: "i-material-symbols:edit-square-outline",
    to: editLink,
  });
  return actions;
});

const mobileMenuItems = computed(() => {
  return [
    [
      {
        label: "Cite",
        icon: "i-material-symbols:verified-outline",
        click: () => {
          isCiteOpen.value = true;
        },
      },
      {
        label: "Export JSON",
        icon: "i-material-symbols:data-object",
        click: exportJSON,
      },
      {
        label: "Print",
        icon: "i-material-symbols:print-outline",
        click: printPage,
      },
      {
        label: "Suggest Edit",
        icon: "i-material-symbols:edit-square-outline",
        click: () => {
          window.open(suggestEditLink.value, "_blank");
        },
      },
    ],
  ];
});

const suggestEditLink = ref("");
const airtableFormID = "appQ32aUep05DxTJn/pagmgHV1lW4UIZVXS/form";

onMounted(() => {
  const currentURL = window.location.href;
  suggestEditLink.value = `https://airtable.com/${airtableFormID}?prefill_URL=${encodeURIComponent(currentURL)}&hide_URL=true`;
});

const legalFamily = computed(() => {
  if (
    props.resultData &&
    (props.cardType === "Jurisdiction" || props.resultData["Legal Family"])
  ) {
    const value = props.resultData["Legal Family"] || "";
    if (!value || value === "N/A") return [];
    return value
      .split(",")
      .map((f) => f.trim())
      .filter((f) => f);
  }
  return [];
});

function getSourceTablePlural(label) {
  if (label === "Court Decision") return "Court Decisions";
  if (label === "Domestic Instrument") return "Domestic Instruments";
  if (label === "Regional Instrument") return "Regional Instruments";
  if (label === "International Instrument") return "International Instruments";
  if (label === "Question") return "Questions";
  if (label === "Arbitral Rule") return "Arbitral Rules";
  if (label === "Arbitral Award") return "Arbitral Awards";
  return label;
}

const typeOptions = [
  { label: "Court Decision", value: "Court Decision" },
  { label: "Domestic Instrument", value: "Domestic Instrument" },
  { label: "Regional Instrument", value: "Regional Instrument" },
  { label: "International Instrument", value: "International Instrument" },
  { label: "Literature", value: "Literature" },
];
const selectedType = ref("");

onMounted(() => {
  if (props.headerMode === "new") {
    selectedType.value = "";
  }
});

watch(
  () => route.fullPath,
  () => {
    if (props.headerMode === "new") {
      selectedType.value = "";
    }
  },
);

function typeToNewPath(label) {
  const slug =
    label === "Court Decision"
      ? "court-decision"
      : label === "Domestic Instrument"
        ? "domestic-instrument"
        : label === "Regional Instrument"
          ? "regional-instrument"
          : label === "International Instrument"
            ? "international-instrument"
            : label === "Question"
              ? "question"
              : "literature";
  return `/${slug}/new`;
}

watch(selectedType, (val, old) => {
  if (props.headerMode === "new" && val && val !== old) {
    router.push(typeToNewPath(val));
  }
});

function sanitizeFilename(filename) {
  return filename
    .replace(/[<>:"/\\|?*]/g, "") // Remove invalid characters
    .replace(/\s+/g, "_") // Replace spaces with underscores
    .substring(0, 200); // Limit length
}

function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function exportJSON() {
  const json = JSON.stringify(props.resultData, null, 2);
  const title =
    props.resultData.Title ||
    props.resultData["Case Title"] ||
    props.resultData.Name ||
    props.resultData["Case Citation"] ||
    "export";
  const filename = `${sanitizeFilename(title)}.json`;
  downloadFile(json, filename, "application/json");
}

function printPage() {
  window.print();
}
</script>

<style scoped>
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.tags-container {
  overflow-x: auto;
  white-space: nowrap;
  flex-grow: 1;
  padding-bottom: 0.25rem;
  padding-top: 0.25rem;
}

.actions-container {
  align-items: center;
  gap: 0.5rem;
}

.actions-container button,
.actions-container a {
  transition: all 0.2s ease;
}

.fade-out-container {
  position: relative;
  flex-shrink: 0;
  width: 50px;
  margin-left: -50px;
  z-index: 1;
}

.fade-out {
  position: absolute;
  top: 0;
  right: 50px;
  width: 60px;
  height: 100%;
  background: linear-gradient(to left, white, transparent);
  pointer-events: none;
  z-index: 10;
}

.fade-out.open-link-true {
  right: 50px;
}

.fade-out.suggest-edit-true {
  right: 266px;
}

.fade-out.open-link-false.suggest-edit-false {
  right: 0;
}

.open-link {
  flex-shrink: 0;
  position: relative;
  z-index: 20;
}

.scrollbar-hidden::-webkit-scrollbar {
  display: none;
}
.scrollbar-hidden {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.gray-link {
  color: var(--color-cold-night-alpha-25) !important;
}

a {
  font-weight: 500 !important;
  text-decoration: none !important;
}

.jurisdiction-label-link {
  font-weight: 600 !important;

  .hover-flag {
    margin-right: 0.375rem;
    margin-bottom: 0.125rem;
  }

  .flag-icon {
    height: 11px;
    width: auto;
  }
}

.label-court-decision,
a.label-court-decision {
  color: var(--color-label-court-decision) !important;
}
.label-question,
a.label-question {
  color: var(--color-label-question) !important;
}
.label-instrument,
a.label-instrument {
  color: var(--color-label-instrument) !important;
}
.label-literature,
a.label-literature {
  color: var(--color-label-literature) !important;
}

.label-arbitration,
a.label-arbitration {
  color: var(--color-label-arbitration) !important;
}

.no-caret-select :deep([class*="i-heroicons-chevron"]) {
  display: none !important;
}
.no-caret-select :deep([class*="i-heroicons-chevron"]) svg {
  display: none !important;
}

.no-caret-select :deep([class*="i-material-symbols\:arrow-drop-down"]) {
  display: none !important;
}

.no-caret-select :deep([class*="i-heroicons-chevron-up-down"]) {
  display: none !important;
}

.no-caret-select :deep(.ui-input-trailing),
.no-caret-select :deep(.u-input-trailing) {
  color: inherit !important;
}

.no-caret-select :deep(.u-input-trailing),
.no-caret-select :deep(.ui-input-trailing) {
  display: inline-flex !important;
  align-items: center !important;
}

.custom-caret {
  display: inline-flex;
  align-items: center;
  margin-left: 0.25rem;
  pointer-events: none;
}

.no-caret-select :deep(select) {
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  appearance: none !important;
  background-image: none !important;
  background: none !important;
}

.no-caret-select :deep(select::-ms-expand) {
  display: none !important;
}

.no-caret-select :deep(.ui-input),
.no-caret-select :deep(.u-input),
.no-caret-select :deep([role="button"]),
.no-caret-select :deep([role="combobox"]) {
  height: 22px !important;
  min-height: 22px !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  line-height: 1 !important;
}
.no-caret-select :deep(.ui-input-trailing),
.no-caret-select :deep(.u-input-trailing) {
  height: 22px !important;
}

.no-caret-select.label :deep(button[role="combobox"]) {
  color: inherit !important;
  font-weight: inherit !important;
  font-size: inherit !important;
  text-transform: inherit !important;
}
.no-caret-select.label :deep(.ui-input),
.no-caret-select.label :deep(.u-input) {
  color: inherit !important;
  font-weight: inherit !important;
  font-size: inherit !important;
  text-transform: inherit !important;
}

.no-caret-select.label :deep(.u-input *),
.no-caret-select.label :deep(.ui-input *),
.no-caret-select.label :deep(button[role="combobox"] *) {
  font-size: inherit !important;
  text-transform: inherit !important;
}

.no-caret-select :deep(button[role="combobox"]) {
  font-size: 12px !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  color: var(--color-cold-purple) !important;
}
.no-caret-select :deep(button[role="combobox"] span),
.no-caret-select :deep(button[role="combobox"] div),
.no-caret-select :deep(.u-input .u-input-value),
.no-caret-select :deep(.ui-input .ui-input-value) {
  font-size: 12px !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  color: var(--color-cold-purple) !important;
}

.no-caret-select :deep(.u-select),
.no-caret-select :deep(.ui-select),
.no-caret-select :deep(.u-input-wrapper),
.no-caret-select :deep(.ui-input-wrapper) {
  height: 22px !important;
}
.no-caret-select :deep(button[role="combobox"]) {
  height: 22px !important;
  min-height: 22px !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

.new-select-label :deep(button[role="combobox"]),
.new-select-label :deep(button[role="combobox"] *),
.new-select-label :deep(.u-input .u-input-value),
.new-select-label :deep(.ui-input .ui-input-value),
.no-caret-select.new-select-label :deep(button[role="combobox"]),
.no-caret-select.new-select-label :deep(button[role="combobox"] *),
.no-caret-select.new-select-label :deep(.u-input .u-input-value),
.no-caret-select.new-select-label :deep(.ui-input .ui-input-value) {
  font-size: 12px !important;
  text-transform: uppercase !important;
  font-weight: 600 !important;
  color: var(--color-cold-purple) !important;
}

.arrow-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
}

.arrow-icon {
  font-size: 1.5rem;
  color: var(--color-cold-purple);
  transition: transform 0.3s ease;
}

/* Mobile menu dropdown styling - matches section-nav-item tabs */
:deep(.mobile-menu-item) {
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-cold-night);
  cursor: pointer;
  transition: all 0.15s ease;
  border-left: 2px solid transparent;
}

:deep(.mobile-menu-item:hover),
:deep(.mobile-menu-item-active) {
  background: var(--gradient-subtle);
  color: var(--color-cold-purple);
  border-left-color: var(--color-cold-purple);
}
</style>
