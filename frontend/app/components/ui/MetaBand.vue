<template>
  <section
    v-if="isVisible"
    class="meta-band"
    :class="{
      'meta-band--new': headerMode === 'new',
      'meta-band--compact': compact,
    }"
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
        <div v-if="hasFirstLine || resolvedTheme.length > 0" class="meta-line">
          <button
            v-if="typeChip && isJurisdictionType"
            ref="typeChipRef"
            type="button"
            :class="[
              'schip',
              'schip--type',
              'schip--button',
              typeChip.colorClass,
            ]"
            :aria-expanded="pickerOpen"
            aria-haspopup="listbox"
            @click="togglePicker"
          >
            <span class="schip-text">{{ typeChip.label }}</span>
          </button>
          <NuxtLink
            v-else-if="typeChip"
            :to="typeChip.to"
            :class="['schip', 'schip--type', typeChip.colorClass]"
          >
            <span class="schip-tag" aria-hidden="true">
              <UIcon name="i-lucide:tag" />
            </span>
            <span class="schip-text">{{ typeChip.label }}</span>
            <span class="schip-affordance" aria-hidden="true">
              <UIcon name="i-material-symbols:search" />
            </span>
          </NuxtLink>
          <NuxtLink
            v-for="(j, idx) in resolvedJurisdiction"
            :key="`jur-${idx}`"
            :to="`/jurisdiction/${j.coldId}`"
            class="schip schip--jur"
          >
            <span class="schip-flag-wrap">
              <JurisdictionFlag
                v-if="j.coldId"
                :iso3="j.coldId"
                class="schip-flag"
              />
            </span>
            <span class="schip-text">{{ j.name }}</span>
            <span class="schip-arrow-wrap" aria-hidden="true">
              <UIcon name="i-material-symbols:arrow-forward" />
            </span>
          </NuxtLink>
          <NuxtLink
            v-for="chip in taggedSearchChips"
            :key="chip.key"
            :to="chip.to"
            :class="chip.class"
          >
            <span class="schip-tag" aria-hidden="true">
              <UIcon name="i-lucide:bookmark" />
            </span>
            <span class="schip-text">{{ chip.label }}</span>
            <span class="schip-affordance" aria-hidden="true">
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
          trailing-icon="i-material-symbols:verified-outline"
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
          trailing-icon="i-material-symbols:data-object"
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
          trailing-icon="i-material-symbols:print-outline"
          class="meta-btn"
          @click.prevent="printPage"
        >
          Print
        </UButton>
        <EntityFeedback
          v-if="entityType && entityId"
          :entity-type="entityType as EntityType"
          :entity-id="entityId"
          :entity-title="entityTitle"
        />
      </template>
    </div>
    <LazyCiteModal v-if="!isNewMode" v-model="isCiteOpen" />

    <Teleport to="body">
      <div
        v-if="pickerOpen"
        class="picker-overlay"
        @click.self="pickerOpen = false"
      >
        <div class="picker-panel" :style="pickerStyle">
          <UInput
            v-model="pickerSearch"
            placeholder="Search a jurisdiction..."
            icon="i-material-symbols:search"
            autofocus
            variant="none"
            class="picker-search"
          />
          <div class="picker-list">
            <button
              v-for="item in pickerFiltered"
              :key="item.coldId || item.name"
              class="picker-item"
              type="button"
              @click="selectPickerJurisdiction(item)"
            >
              <JurisdictionFlag
                v-if="item.coldId"
                :iso3="item.coldId"
                :faded="!hasCoverage(item.answerCoverage)"
                class="picker-flag"
              />
              <span
                :class="{
                  'picker-item-text--faded': !hasCoverage(item.answerCoverage),
                }"
              >
                {{ item.label }}
              </span>
            </button>
            <div v-if="pickerFiltered.length === 0" class="picker-empty">
              No jurisdictions found
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch, defineAsyncComponent } from "vue";
import { useRoute, useRouter } from "vue-router";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import type { components } from "@/types/api-schema";
import {
  useJurisdictionLookup,
  useJurisdictions,
} from "@/composables/useJurisdictions";
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

type EntityType = components["schemas"]["EntityType"];

const LazyCiteModal = defineAsyncComponent(
  () => import("@/components/ui/CiteModal.vue"),
);

const props = withDefaults(
  defineProps<{
    resultData?: Record<string, unknown>;
    cardType?: string;
    formattedJurisdiction?: string[];
    formattedTheme?: string[];
    headerMode?: string;
    showCite?: boolean;
    showJson?: boolean;
    showPrint?: boolean;
    entityType?: string;
    entityId?: string;
    entityTitle?: string;
    compact?: boolean;
  }>(),
  {
    resultData: () => ({}),
    cardType: "",
    formattedJurisdiction: () => [],
    formattedTheme: () => [],
    headerMode: "default",
    showCite: true,
    showJson: true,
    showPrint: true,
    entityType: "",
    entityId: "",
    entityTitle: "",
    compact: false,
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

const searchParam = (value: string) =>
  encodeURIComponent(value).replace(/%20/g, "+");

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

  const primary = findJurisdictionByCode(
    primaryJurisdictionAlpha3(props.resultData),
  );
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
    to: `/search?type=${searchParam(searchType)}`,
  };
});

interface TaggedSearchChip {
  key: string;
  to: string;
  class: string;
  label: string;
}

const taggedSearchChips = computed<TaggedSearchChip[]>(() =>
  resolvedTheme.value.map((theme, idx) => ({
    key: `theme-${idx}`,
    to: `/search?theme=${searchParam(theme)}`,
    class: "schip schip--theme",
    label: theme,
  })),
);

const isJurisdictionType = computed(
  () => typeChip.value?.colorClass === "label-jurisdiction",
);

const { data: allJurisdictions } = useJurisdictions(isJurisdictionType);

const typeChipRef = ref<HTMLButtonElement | null>(null);
const pickerOpen = ref(false);
const pickerSearch = ref("");
const pickerStyle = ref<Record<string, string>>({});

const hasCoverage = (coverage?: number) => (coverage ?? 0) > 0;

const pickerFiltered = computed(() => {
  const list = allJurisdictions.value ?? [];
  const q = pickerSearch.value.toLowerCase().trim();
  if (!q) return list;
  return list.filter((j) => j.label.toLowerCase().includes(q));
});

watch(pickerOpen, async (open) => {
  if (open) {
    await nextTick();
    positionPicker();
  } else {
    pickerSearch.value = "";
  }
});

watch(
  () => route.fullPath,
  () => {
    pickerOpen.value = false;
    if (props.headerMode === "new") selectedNewType.value = "";
  },
);

function togglePicker() {
  pickerOpen.value = !pickerOpen.value;
}

function positionPicker() {
  const el = typeChipRef.value;
  if (!el) return;
  const rect = el.getBoundingClientRect();
  const offset = 4;
  const collisionPadding = 8;
  const availableHeight =
    window.innerHeight - rect.bottom - offset - collisionPadding;
  pickerStyle.value = {
    top: `${rect.bottom + offset}px`,
    left: `${rect.left}px`,
    minWidth: `${Math.max(rect.width, 260)}px`,
    maxHeight: `${availableHeight}px`,
  };
}

function selectPickerJurisdiction(item: { coldId?: string }) {
  pickerOpen.value = false;
  if (!item.coldId) return;
  router.push(`/jurisdiction/${item.coldId.toUpperCase()}`);
}

const hasFirstLine = computed(
  () => !!typeChip.value || resolvedJurisdiction.value.length > 0,
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
  return (
    props.showCite ||
    props.showJson ||
    props.showPrint ||
    !!(props.entityType && props.entityId)
  );
});

const typeOptions = [
  { label: "Court Decision", value: "Court Decision" },
  { label: "Domestic Instrument", value: "Domestic Instrument" },
  { label: "Regional Instrument", value: "Regional Instrument" },
  { label: "International Instrument", value: "International Instrument" },
  { label: "Literature", value: "Literature" },
];
const selectedNewType = ref("");

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
  background: var(--gradient-subtle);
  border-bottom: 1px solid
    color-mix(in srgb, var(--color-cold-gray) 70%, transparent);
}

@media (max-width: 640px) {
  .meta-band {
    grid-template-columns: 1fr;
    padding: 0.625rem 1rem;
  }
}

.meta-band--compact {
  grid-template-columns: 1fr;
  padding: 0 0.875rem 0.625rem;
  background: transparent;
  border-bottom: none;
}

.meta-band--compact .meta-chips {
  gap: 5px;
}

.meta-band--compact .meta-line {
  gap: 5px 7px;
  min-height: 0;
}

.meta-band--compact .schip {
  font-size: 10px;
  letter-spacing: 0.04em;
  padding: 1px 7px;
  gap: 4px;
}

.meta-band--compact .schip-flag-wrap,
.meta-band--compact .schip-arrow-wrap {
  width: 14px;
  height: 10px;
}

.meta-band--compact .schip-arrow-wrap {
  width: 0;
}

.meta-band--compact .schip--jur:hover .schip-arrow-wrap {
  width: 14px;
}

.meta-band--compact .schip-flag {
  width: 14px;
  height: 10px;
}

.meta-band--compact .schip-tag,
.meta-band--compact .schip-affordance {
  font-size: 10px;
}

.meta-band--compact .schip-tag {
  width: 10px;
}

.meta-band--compact .schip:hover .schip-tag {
  width: 0;
}

.meta-band--compact .schip:hover .schip-affordance {
  width: 10px;
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

.meta-label {
  font-family: "IBM Plex Mono", monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-cold-night-alpha);
  flex-shrink: 0;
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

.schip--button {
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  margin: 0;
}

.schip--jur {
  --schip-color: var(--color-cold-night);
}

.schip--theme {
  --schip-color: var(--color-cold-purple);
}

.schip-flag-wrap,
.schip-arrow-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 16px;
  height: 11px;
  overflow: hidden;
  transition:
    width 0.18s ease,
    opacity 0.15s ease;
}

.schip-flag {
  width: 16px;
  height: 11px;
  object-fit: contain;
}

.schip-arrow-wrap {
  width: 0;
  opacity: 0;
  font-size: 12px;
}

.schip--jur:hover .schip-flag-wrap {
  width: 0;
  opacity: 0;
}

.schip--jur:hover .schip-arrow-wrap {
  width: 16px;
  opacity: 0.9;
}

.schip-tag,
.schip-affordance {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 11px;
  font-size: 11px;
  overflow: hidden;
  transition:
    width 0.15s ease,
    opacity 0.15s ease;
}

.schip-tag {
  opacity: 0.65;
}

.schip-affordance {
  width: 0;
  opacity: 0;
}

.schip:hover .schip-tag {
  width: 0;
  opacity: 0;
}

.schip:hover .schip-affordance {
  width: 11px;
  opacity: 0.9;
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

<style>
.picker-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
}

.picker-panel {
  position: fixed;
  width: 300px;
  max-width: calc(100vw - 1rem);
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 0.5rem;
  border: 1px solid var(--color-cold-gray);
  box-shadow:
    0 4px 12px rgb(0 0 0 / 0.08),
    0 1px 3px rgb(0 0 0 / 0.04);
  z-index: 101;
}

.picker-search {
  border-bottom: 1px solid var(--color-cold-gray);
}

.picker-search :deep(input) {
  text-align: left;
}

.picker-list {
  overflow-y: auto;
  padding: 0.25rem;
}

.picker-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.625rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-family: "DM Sans", sans-serif;
  color: var(--color-cold-night);
  text-align: left;
  cursor: pointer;
  transition: background 0.1s ease;
  border: none;
  background: none;
}

.picker-item:hover {
  background: var(--gradient-subtle-hover);
}

.picker-flag {
  flex-shrink: 0;
}

.picker-item-text--faded {
  color: var(--color-cold-night-alpha);
}

.picker-empty {
  padding: 1rem;
  text-align: center;
  font-size: 0.875rem;
  color: var(--color-cold-slate);
}
</style>
