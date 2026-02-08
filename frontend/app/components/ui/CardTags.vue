<template>
  <div
    class="tags-container scrollbar-hidden flex flex-1 flex-wrap items-center overflow-x-auto"
  >
    <NuxtLink
      v-for="(jurisdictionString, index) in formattedJurisdiction"
      :key="`jurisdiction-${index}`"
      class="label-jurisdiction jurisdiction-label-link"
      :to="`/search?jurisdiction=${encodeURIComponent(jurisdictionString).replace(/%20/g, '+')}`"
      @click.stop
    >
      <span class="flag-wrapper">
        <JurisdictionFlag
          :iso3="getJurisdictionISO(jurisdictionString)"
          class="flag-icon"
        />
      </span>
      {{ jurisdictionString }}
    </NuxtLink>

    <span
      v-for="(family, index) in legalFamily"
      :key="`legal-family-${index}`"
      class="label-theme"
    >
      {{ family }}
    </span>

    <template
      v-if="
        sourceTableLabel &&
        !['Jurisdiction', 'Jurisdictions'].includes(sourceTableLabel)
      "
    >
      <div v-if="headerMode === 'new'" class="flex items-center">
        <span :class="['label', labelColorClass]">
          {{ sourceTableLabel }}
        </span>
        <div class="-ml-2">
          <USelect
            v-model="selectedType"
            variant="none"
            placeholder=" "
            :items="typeOptions"
            value-key="value"
            label-key="label"
            class="leading-none"
            :ui="{
              base: 'h-[22px] min-h-[22px] py-0 text-xs font-bold uppercase text-[var(--color-cold-purple)] leading-none',
              trailingIcon: 'hidden',
            }"
          >
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
      <template v-else>
        <span
          v-if="
            ['Arbitral Rule', 'Arbitral Award', 'Jurisdiction'].includes(
              sourceTableLabel,
            )
          "
          :class="['label', labelColorClass]"
        >
          {{ sourceTableLabel }}
        </span>
        <NuxtLink
          v-else
          :to="
            '/search?type=' +
            encodeURIComponent(getSourceTablePlural(sourceTableLabel)).replace(
              /%20/g,
              '+',
            )
          "
          :class="['label', labelColorClass, 'label-link', 'cursor-pointer']"
        >
          {{ sourceTableLabel }}
        </NuxtLink>
      </template>
    </template>

    <UButton
      v-for="(theme, index) in formattedTheme"
      :key="`theme-${index}`"
      :to="'/search?theme=' + encodeURIComponent(theme).replace(/%20/g, '+')"
      variant="link"
      color="neutral"
      trailing-icon="i-material-symbols:arrow-forward"
      class="label-theme group"
      :ui="{
        base: 'gap-0 transition-[margin-right] duration-200 hover:mr-[-1rem]',
        trailingIcon:
          'h-3 w-0 ml-0 shrink-0 opacity-0 transition-[width,margin,opacity] duration-200 group-hover:w-3 group-hover:ml-1 group-hover:opacity-100',
      }"
      @click.stop
    >
      {{ theme }}
    </UButton>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";
import { useJurisdictionLookup } from "@/composables/useJurisdictions";

const props = defineProps({
  formattedJurisdiction: {
    type: Array,
    default: () => [],
  },
  formattedTheme: {
    type: Array,
    default: () => [],
  },
  legalFamily: {
    type: Array,
    default: () => [],
  },
  sourceTableLabel: {
    type: String,
    default: "",
  },
  labelColorClass: {
    type: String,
    default: "",
  },
  headerMode: {
    type: String,
    default: "default",
  },
});

const route = useRoute();
const router = useRouter();

const { getJurisdictionISO } = useJurisdictionLookup();

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
</script>

<style scoped>
.tags-container {
  overflow-x: auto;
  white-space: nowrap;
  flex-grow: 1;
  padding-bottom: 0.25rem;
  padding-top: 0.25rem;
}

.tags-container > * {
  margin-right: 0.625rem;
}

.tags-container > *:last-child {
  margin-right: 0;
}

.scrollbar-hidden::-webkit-scrollbar {
  display: none;
}
.scrollbar-hidden {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

a {
  font-weight: 500 !important;
  text-decoration: none !important;
}

.jurisdiction-label-link {
  font-weight: 600 !important;

  .flag-wrapper {
    width: 1.125rem;
  }

  .flag-icon {
    height: 11px;
    width: auto;
  }
}

.jurisdiction-label-link:hover .flag-wrapper {
  width: 0;
  opacity: 0;
}

.jurisdiction-label-link::after {
  mask-image: var(--icon-search);
  -webkit-mask-image: var(--icon-search);
  height: 0.75rem;
}

.jurisdiction-label-link:hover::after {
  width: 1.125rem;
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

.custom-caret {
  display: inline-flex;
  align-items: center;
  margin-left: 0.25rem;
  pointer-events: none;
}
</style>
