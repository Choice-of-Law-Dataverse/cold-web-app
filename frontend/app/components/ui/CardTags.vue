<template>
  <div
    class="tags-container scrollbar-hidden flex flex-1 flex-wrap items-center overflow-x-auto"
  >
    <NuxtLink
      v-for="(jurisdictionString, index) in formattedJurisdiction"
      :key="`jurisdiction-${index}`"
      class="schip schip--jur"
      :to="jurisdictionLinkTo(jurisdictionString)"
      @click.stop
    >
      <JurisdictionFlag
        :iso3="getJurisdictionISO(jurisdictionString)"
        class="schip-flag"
      />
      <span class="schip-text">{{ jurisdictionString }}</span>
      <span class="schip-affordance schip-affordance--arrow">
        <UIcon name="i-material-symbols:arrow-forward" />
      </span>
    </NuxtLink>

    <span
      v-for="(family, index) in legalFamily"
      :key="`legal-family-${index}`"
      class="schip schip--family"
    >
      <span class="schip-text">{{ family }}</span>
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
                    stroke-linejoin="miter"
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
            [
              'Arbitral Rule',
              'Arbitral Award',
              'Jurisdiction',
              'Specialist',
            ].includes(sourceTableLabel)
          "
          :class="['schip', 'schip--type', labelColorClass]"
        >
          <span class="schip-text">{{ sourceTableLabel }}</span>
        </span>
        <NuxtLink
          v-else
          :to="
            '/search?type=' +
            encodeURIComponent(getTableName(sourceTableLabel)).replace(
              /%20/g,
              '+',
            )
          "
          :class="['schip', 'schip--type', labelColorClass]"
        >
          <span class="schip-text">{{ sourceTableLabel }}</span>
        </NuxtLink>
      </template>
    </template>

    <NuxtLink
      v-for="(theme, index) in formattedTheme"
      :key="`theme-${index}`"
      class="schip schip--theme"
      :to="'/search?theme=' + encodeURIComponent(theme).replace(/%20/g, '+')"
    >
      <span class="schip-text">{{ theme }}</span>
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";
import { useJurisdictionLookup } from "@/composables/useJurisdictions";
import { getBasePathForCard, getTableName } from "@/config/entityRegistry";

const props = withDefaults(
  defineProps<{
    formattedJurisdiction?: string[];
    formattedTheme?: string[];
    legalFamily?: string[];
    sourceTableLabel?: string;
    labelColorClass?: string;
    headerMode?: string;
  }>(),
  {
    formattedJurisdiction: () => [],
    formattedTheme: () => [],
    legalFamily: () => [],
    sourceTableLabel: "",
    labelColorClass: "",
    headerMode: "default",
  },
);

const route = useRoute();
const router = useRouter();

const { getJurisdictionISO, findJurisdictionByName } = useJurisdictionLookup();

function jurisdictionLinkTo(name: string): string {
  const match = findJurisdictionByName(name);
  if (match?.coldId) return `/jurisdiction/${match.coldId}`;
  return `/search?jurisdiction=${encodeURIComponent(name).replace(/%20/g, "+")}`;
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

function typeToNewPath(label: string): string {
  const basePath = getBasePathForCard(label) ?? "/literature";
  return `${basePath}/new`;
}

watch(selectedType, (val, old) => {
  if (props.headerMode === "new" && val && val !== old) {
    router.push(typeToNewPath(val));
  }
});
</script>

<style scoped>
.tags-container {
  overflow-x: auto;
  white-space: nowrap;
  flex-grow: 1;
  padding-bottom: 0.25rem;
  padding-top: 0.25rem;
  gap: 6px 8px;
}

.tags-container > * {
  margin-right: 0.5rem;
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

.schip {
  --schip-color: var(--color-cold-purple);
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-family: "IBM Plex Mono", monospace;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 2px 9px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--schip-color) 8%, white);
  color: color-mix(in srgb, var(--schip-color) 80%, black);
  text-decoration: none;
  white-space: nowrap;
  border: 1px solid transparent;
  transition:
    background 0.15s ease,
    border-color 0.15s ease,
    color 0.15s ease;
}

.schip:hover {
  background: color-mix(in srgb, var(--schip-color) 14%, white);
  border-color: color-mix(in srgb, var(--schip-color) 30%, white);
  color: color-mix(in srgb, var(--schip-color) 95%, black);
}

.schip--type {
  --schip-color: var(--color-cold-purple);
}

.schip--type.label-court-decision {
  --schip-color: var(--color-label-court-decision);
}
.schip--type.label-question {
  --schip-color: var(--color-label-question);
}
.schip--type.label-instrument {
  --schip-color: var(--color-label-instrument);
}
.schip--type.label-arbitration {
  --schip-color: var(--color-label-arbitration);
}
.schip--type.label-literature {
  --schip-color: var(--color-label-literature);
}
.schip--type.label-specialist {
  --schip-color: var(--color-label-specialist);
}
.schip--type.label-jurisdiction {
  --schip-color: var(--color-cold-night);
}

.schip--jur {
  --schip-color: var(--color-cold-night);
}

.schip--family {
  --schip-color: #b07000;
  background: transparent;
  font-weight: 500;
}

.schip--family:hover {
  background: color-mix(in srgb, var(--schip-color) 10%, white);
}

.schip--theme {
  --schip-color: var(--color-cold-purple);
}

.schip-flag {
  height: 11px;
  width: auto;
  transition:
    opacity 0.15s ease,
    width 0.15s ease;
}

.schip--jur:hover .schip-flag {
  opacity: 0;
  width: 0;
  margin-right: -5px;
}

.schip-affordance {
  display: inline-flex;
  align-items: center;
  width: 0;
  opacity: 0;
  margin-left: -2px;
  font-size: 11px;
  transition:
    opacity 0.15s ease,
    width 0.15s ease,
    margin 0.15s ease;
}

.schip--jur:hover .schip-affordance--arrow {
  width: 11px;
  opacity: 0.9;
  margin-left: 2px;
}

.custom-caret {
  display: inline-flex;
  align-items: center;
  margin-left: 0.25rem;
  pointer-events: none;
}
</style>
