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
          <SchipType
            v-if="typeChip && isJurisdictionType"
            ref="typeChipRef"
            as-button
            :color-class="typeChip.colorClass"
            :compact="compact"
            :aria-expanded="pickerOpen"
            aria-haspopup="listbox"
            @click="togglePicker"
          >
            {{ typeChip.label }}
          </SchipType>
          <SchipType
            v-else-if="typeChip && typeChip.to"
            :color-class="typeChip.colorClass"
            :to="typeChip.to"
            :compact="compact"
          >
            {{ typeChip.label }}
          </SchipType>
          <SchipType
            v-else-if="typeChip"
            is-static
            :color-class="typeChip.colorClass"
            :compact="compact"
          >
            {{ typeChip.label }}
          </SchipType>
          <SchipJurisdiction
            v-for="(j, idx) in resolvedJurisdiction"
            :key="`jur-${idx}`"
            :iso3="j.coldId"
            :to="`/jurisdiction/${j.coldId}`"
            :compact="compact"
          >
            {{ j.name }}
          </SchipJurisdiction>
          <SchipTheme
            v-for="theme in resolvedTheme"
            :key="`theme-${theme}`"
            :to="`/search?theme=${searchParam(theme)}`"
            :compact="compact"
          >
            {{ theme }}
          </SchipTheme>
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
          v-if="showNew && newEntityHref && isLoggedIn"
          :to="newEntityHref"
          variant="ghost"
          color="neutral"
          size="xs"
          leading-icon="i-material-symbols:add"
          trailing-icon="i-material-symbols:add"
          class="meta-btn"
        >
          New
        </UButton>
        <UPopover
          v-else-if="showNew && newEntityHref"
          :content="{ side: 'bottom', align: 'end', sideOffset: 8 }"
        >
          <UButton
            variant="ghost"
            color="neutral"
            size="xs"
            leading-icon="i-material-symbols:lock-outline"
            trailing-icon="i-material-symbols:lock-outline"
            class="meta-btn"
            aria-label="Sign in to add new entry"
          >
            Submit data
          </UButton>
          <template #content>
            <div class="login-popover">
              <p class="login-popover__text">
                A free CoLD account is required to keep the dataverse
                trustworthy &mdash; we use it to prevent automated spam and
                preserve the integrity of every record. Sign-up takes under a
                minute.
              </p>
              <UButton
                :to="loginRedirectHref"
                external
                block
                color="primary"
                size="sm"
                leading-icon="i-material-symbols:login"
              >
                Sign in to continue
              </UButton>
            </div>
          </template>
        </UPopover>
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
import SchipType from "@/components/ui/SchipType.vue";
import SchipTheme from "@/components/ui/SchipTheme.vue";
import SchipJurisdiction from "@/components/ui/SchipJurisdiction.vue";
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
  getIndexPathForCard,
  getLabelColorClass,
  getNewPathForCard,
  getSingularLabel,
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
    showNew?: boolean;
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
    showNew: true,
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
const user = useUser();
const { findJurisdictionByCode, findJurisdictionByName } =
  useJurisdictionLookup();

const isCiteOpen = ref(false);
const isNewMode = computed(() => props.headerMode === "new");
const isLoggedIn = computed(() => !!user.value);

const newEntityHref = computed(() => {
  if (props.headerMode === "new") return undefined;
  const cardType =
    props.cardType || String(props.resultData?.sourceTable ?? "");
  if (!cardType) return undefined;
  const indexPath = getIndexPathForCard(cardType);
  const newPath = getNewPathForCard(cardType);
  if (!indexPath || !newPath) return undefined;
  if (route.path.replace(/\/$/, "") !== indexPath) return undefined;
  return newPath;
});

const loginRedirectHref = computed(() =>
  newEntityHref.value
    ? `/auth/login?returnTo=${encodeURIComponent(newEntityHref.value)}`
    : undefined,
);

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

  const relations = (props.resultData as { relations?: unknown }).relations;
  const relationThemes =
    relations &&
    typeof relations === "object" &&
    Array.isArray((relations as { themes?: unknown }).themes)
      ? (relations as { themes: Array<{ theme?: string | null }> }).themes
          .map((t) => t?.theme?.trim())
          .filter((t): t is string => !!t && t !== "null" && t !== "None")
      : [];
  if (relationThemes.length > 0) return [...new Set(relationThemes)];

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
  return {
    label,
    colorClass,
    to: getIndexPathForCard(cardType) ?? "",
  };
});

const isJurisdictionType = computed(
  () => typeChip.value?.colorClass === "label-jurisdiction",
);

const { data: allJurisdictions } = useJurisdictions(isJurisdictionType);

const typeChipRef = ref<InstanceType<typeof SchipType> | null>(null);
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
  const el = typeChipRef.value?.rootEl ?? null;
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
    (props.showNew && !!newEntityHref.value) ||
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

.login-popover {
  width: 20rem;
  max-width: calc(100vw - 1rem);
  padding: 0.875rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.login-popover__text {
  font-family: "DM Sans", sans-serif;
  font-size: 0.8125rem;
  line-height: 1.5;
  color: var(--color-cold-night-alpha);
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
