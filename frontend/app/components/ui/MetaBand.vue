<template>
  <section
    v-if="isVisible"
    class="meta-band"
    :class="{ 'meta-band--new': headerMode === 'new' }"
  >
    <div class="meta-chips">
      <template v-if="headerMode === 'new'">
        <div class="meta-line">
          <span class="meta-label">Type</span>
          <USelect
            v-model="selectedNewType"
            variant="none"
            placeholder="Select type"
            :items="typeOptions"
            value-key="value"
            label-key="label"
            class="leading-none"
            :ui="{
              base: 'h-[24px] min-h-[24px] py-0 text-xs font-bold uppercase text-[var(--color-cold-purple)] leading-none bg-[color-mix(in_srgb,var(--color-cold-purple)_12%,white)] rounded',
              trailingIcon: 'text-[var(--color-cold-purple)]',
            }"
          />
        </div>
      </template>
      <template v-else>
        <div v-if="hasFirstLine" class="meta-line">
          <NuxtLink
            v-if="typeChip"
            :to="typeChip.to"
            :class="['schip', 'schip--type', typeChip.colorClass]"
          >
            <span class="schip-text">{{ typeChip.label }}</span>
            <span class="schip-affordance schip-affordance--search">
              <UIcon name="i-material-symbols:search" />
            </span>
          </NuxtLink>
          <NuxtLink
            v-for="(j, idx) in resolvedJurisdiction"
            :key="`jur-${idx}`"
            :to="`/jurisdiction/${j.coldId}`"
            class="schip schip--jur"
          >
            <JurisdictionFlag
              v-if="j.coldId"
              :iso3="j.coldId"
              class="schip-flag"
            />
            <span class="schip-text">{{ j.name }}</span>
            <span class="schip-affordance schip-affordance--arrow">
              <UIcon name="i-material-symbols:arrow-forward" />
            </span>
          </NuxtLink>
          <NuxtLink
            v-for="(f, idx) in resolvedLegalFamily"
            :key="`family-${idx}`"
            :to="`/search?type=Jurisdictions&legalFamily=${encodeURIComponent(f).replace(/%20/g, '+')}`"
            class="schip schip--family"
          >
            <span class="schip-text">{{ f }}</span>
            <span class="schip-affordance schip-affordance--search">
              <UIcon name="i-material-symbols:search" />
            </span>
          </NuxtLink>
        </div>
        <div v-if="resolvedTheme.length > 0" class="meta-line">
          <NuxtLink
            v-for="(theme, idx) in resolvedTheme"
            :key="`theme-${idx}`"
            :to="`/search?theme=${encodeURIComponent(theme).replace(/%20/g, '+')}`"
            class="schip schip--theme"
          >
            <span class="schip-text">{{ theme }}</span>
            <span class="schip-affordance schip-affordance--search">
              <UIcon name="i-material-symbols:search" />
            </span>
          </NuxtLink>
        </div>
      </template>
    </div>

    <div v-if="hasActions" class="meta-actions">
      <template v-if="headerMode === 'new'">
        <UButton color="primary" size="xs" @click="emit('open-save-modal')">
          Submit your data
        </UButton>
      </template>
      <template v-else>
        <UButton
          v-if="showCite"
          variant="ghost"
          color="neutral"
          size="xs"
          leading-icon="i-material-symbols:verified-outline"
          class="meta-btn"
          @click.prevent="isCiteOpen = true"
        >
          Cite
        </UButton>
        <UButton
          v-if="showJson"
          variant="ghost"
          color="neutral"
          size="xs"
          leading-icon="i-material-symbols:data-object"
          class="meta-btn"
          @click.prevent="exportJSON"
        >
          JSON
        </UButton>
        <UButton
          v-if="showPrint"
          variant="ghost"
          color="neutral"
          size="xs"
          leading-icon="i-material-symbols:print-outline"
          class="meta-btn"
          @click.prevent="printPage"
        >
          Print
        </UButton>
      </template>
    </div>
    <LazyCiteModal v-if="!isNewMode" v-model="isCiteOpen" />
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch, defineAsyncComponent } from "vue";
import { useRoute, useRouter } from "vue-router";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";
import { useJurisdictionLookup } from "@/composables/useJurisdictions";
import {
  parseJurisdictionString,
  primaryJurisdictionAlpha3,
} from "@/utils/jurisdictionParser";
import {
  getBasePathForCard,
  getLabelColorClass,
  getSingularLabel,
  getTableName,
} from "@/config/entityRegistry";

const LazyCiteModal = defineAsyncComponent(
  () => import("@/components/ui/CiteModal.vue"),
);

const props = withDefaults(
  defineProps<{
    resultData?: Record<string, unknown>;
    cardType?: string;
    formattedJurisdiction?: string[];
    formattedTheme?: string[];
    legalFamily?: string[];
    headerMode?: string;
    showCite?: boolean;
    showJson?: boolean;
    showPrint?: boolean;
    showLegalFamily?: boolean;
  }>(),
  {
    resultData: () => ({}),
    cardType: "",
    formattedJurisdiction: () => [],
    formattedTheme: () => [],
    legalFamily: () => [],
    headerMode: "default",
    showCite: true,
    showJson: true,
    showPrint: true,
    showLegalFamily: true,
  },
);

const emit = defineEmits<{
  "open-save-modal": [];
}>();

const route = useRoute();
const router = useRouter();
const { findJurisdictionByCode, findJurisdictionByName } =
  useJurisdictionLookup();

const isCiteOpen = ref(false);
const isNewMode = computed(() => props.headerMode === "new");

const primaryCode = computed(() => primaryJurisdictionAlpha3(props.resultData));

interface ResolvedJurisdiction {
  name: string;
  coldId: string;
}

const resolvedJurisdiction = computed<ResolvedJurisdiction[]>(() => {
  const fromProps = props.formattedJurisdiction ?? [];
  if (fromProps.length > 0) {
    return fromProps
      .map((name) => {
        const match = findJurisdictionByName(name);
        return {
          name,
          coldId: match?.coldId ?? "",
        };
      })
      .filter((j) => j.coldId);
  }
  const jurisdictionString = String(
    props.resultData.jurisdictionName ||
      props.resultData.jurisdictionNames ||
      props.resultData.nameFromJurisdiction ||
      props.resultData.jurisdiction ||
      props.resultData.jurisdictions ||
      props.resultData.instrument ||
      "",
  );
  const parsed = jurisdictionString
    ? parseJurisdictionString(jurisdictionString)
    : [];

  if (parsed.length === 1) {
    const single = parsed[0];
    if (single == null) return [];
    const match = findJurisdictionByName(single);
    return match?.coldId ? [{ name: single, coldId: match.coldId }] : [];
  }

  const primary = findJurisdictionByCode(primaryCode.value);
  if (primary?.name && primary.coldId) {
    if (parsed.length === 0) {
      return [{ name: primary.name, coldId: primary.coldId }];
    }
    const match = parsed.find(
      (name) => name.toLowerCase() === primary.name.toLowerCase(),
    );
    if (match) return [{ name: match, coldId: primary.coldId }];
  }
  return [];
});

const resolvedLegalFamily = computed<string[]>(() => {
  if (!props.showLegalFamily) return [];
  if (props.legalFamily.length > 0) return props.legalFamily;
  const value = String(props.resultData.legalFamily || "");
  if (!value || value === "N/A") return [];
  return value
    .split(",")
    .map((f) => f.trim())
    .filter((f) => f);
});

const resolvedTheme = computed<string[]>(() => {
  const fromProps = props.formattedTheme ?? [];
  if (fromProps.length > 0) return fromProps;
  if (props.cardType === "Literature" && props.resultData.themes) {
    return String(props.resultData.themes)
      .split(/[,|]/)
      .map((theme) => theme.trim())
      .filter((t) => t && t !== "null" && t !== "None");
  }
  const themes =
    props.resultData.titleOfTheProvision ?? props.resultData.themes;
  if (!themes || themes === "None" || themes === "null") return [];
  return [
    ...new Set(
      String(themes)
        .split(/[,|]/)
        .map((theme) => theme.trim())
        .filter((t) => t && t !== "null" && t !== "None"),
    ),
  ];
});

const typeChip = computed(() => {
  const cardType =
    props.cardType || String(props.resultData?.sourceTable ?? "");
  if (!cardType) return null;
  const colorClass = getLabelColorClass(cardType);
  if (colorClass === "hidden") return null;
  const label = getSingularLabel(cardType);
  if (!label) return null;
  const searchType = getTableName(cardType);
  return {
    label,
    colorClass,
    to: `/search?type=${encodeURIComponent(searchType).replace(/%20/g, "+")}`,
  };
});

const hasFirstLine = computed(
  () =>
    !!typeChip.value ||
    resolvedJurisdiction.value.length > 0 ||
    resolvedLegalFamily.value.length > 0,
);

const hasAnyChips = computed(
  () => hasFirstLine.value || resolvedTheme.value.length > 0,
);

const isVisible = computed(() => {
  if (props.headerMode === "new") return true;
  return hasActions.value || hasAnyChips.value;
});

const hasActions = computed(() => {
  if (props.headerMode === "new") return true;
  return props.showCite || props.showJson || props.showPrint;
});

const typeOptions = [
  { label: "Court Decision", value: "Court Decision" },
  { label: "Domestic Instrument", value: "Domestic Instrument" },
  { label: "Regional Instrument", value: "Regional Instrument" },
  { label: "International Instrument", value: "International Instrument" },
  { label: "Literature", value: "Literature" },
];
const selectedNewType = ref("");

watch(
  () => route.fullPath,
  () => {
    if (props.headerMode === "new") selectedNewType.value = "";
  },
);

watch(selectedNewType, (val, old) => {
  if (props.headerMode === "new" && val && val !== old) {
    const basePath = getBasePathForCard(val) ?? "/literature";
    router.push(`${basePath}/new`);
  }
});

function sanitizeFilename(filename: string): string {
  return filename
    .replace(/[<>:"/\\|?*]/g, "")
    .replace(/\s+/g, "_")
    .substring(0, 200);
}

function downloadFile(
  content: string,
  filename: string,
  mimeType: string,
): void {
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
  const title = String(
    props.resultData.title ||
      props.resultData.caseTitle ||
      props.resultData.name ||
      props.resultData.caseCitation ||
      "export",
  );
  const filename = `${sanitizeFilename(title)}.json`;
  downloadFile(json, filename, "application/json");
}

function printPage() {
  window.print();
}
</script>

<style scoped>
.meta-band {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 6px 18px;
  align-items: center;
  padding: 0.625rem 1rem 0.625rem 1.5rem;
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-purple) 3%, white),
    color-mix(in srgb, var(--color-cold-green) 2%, white)
  );
  border-bottom: 1px solid
    color-mix(in srgb, var(--color-cold-gray) 70%, transparent);
}

@media (max-width: 640px) {
  .meta-band {
    grid-template-columns: 1fr;
    padding: 0.625rem 1rem;
  }
}

.meta-chips {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.meta-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 12px;
  min-height: 22px;
}

.meta-line--empty {
  min-height: 22px;
}

.meta-label {
  font-family: "IBM Plex Mono", monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-cold-night-alpha);
  flex-shrink: 0;
}

.meta-label--muted {
  color: var(--color-cold-night-alpha-25);
}

.meta-sep {
  color: var(--color-cold-night-alpha-25);
  user-select: none;
  font-size: 12px;
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

.schip:hover .schip-affordance {
  width: 11px;
  opacity: 0.9;
  margin-left: 2px;
}

.meta-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}

@media (max-width: 640px) {
  .meta-actions {
    justify-self: end;
  }
}

:deep(.meta-btn) {
  background: transparent;
}

:deep(.meta-btn:hover) {
  background: color-mix(in srgb, var(--color-cold-purple) 6%, white);
}
</style>
