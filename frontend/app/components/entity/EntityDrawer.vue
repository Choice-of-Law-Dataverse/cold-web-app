<template>
  <USlideover
    v-model:open="isOpen"
    side="right"
    :overlay="false"
    :modal="false"
    :dismissible="false"
    :ui="{
      content:
        'sm:max-w-sm max-w-full shadow-2xl !top-[calc(var(--nav-height)+3rem)] !h-auto !bottom-0 rounded-tl-xl',
    }"
  >
    <template #content>
      <div class="flex h-full flex-col">
        <div class="flex items-center justify-between px-6 py-5">
          <a
            v-if="headerJurisdiction"
            class="label-jurisdiction mr-2 truncate"
            :href="`/jurisdiction/${headerJurisdictionCode}`"
            @click="handleJurisdictionClick"
          >
            <div class="flag-wrapper">
              <JurisdictionFlag
                :iso3="headerJurisdictionCode"
                class="item-flag"
                :alt="headerJurisdiction + ' flag'"
              />
            </div>
            <span>{{ headerJurisdiction }}</span>
          </a>
          <span v-else />
          <div class="flex shrink-0 items-center gap-1">
            <UButton
              v-if="hasDetailPage"
              :to="fullPagePath"
              leading-icon="i-lucide-external-link"
              trailing-icon="i-lucide-external-link"
              variant="outline"
              color="neutral"
              size="xs"
              @click="closeDrawer"
            >
              Open
            </UButton>
            <UButton
              icon="i-lucide-x"
              variant="ghost"
              color="neutral"
              size="sm"
              @click="closeDrawer"
            />
          </div>
        </div>

        <div class="gradient-top-border" />

        <div class="flex-1 overflow-y-auto">
          <div v-if="isLoading" class="p-6">
            <LoadingBar />
          </div>
          <InlineError v-else-if="queryError" :error="queryError" class="p-6" />
          <div v-else-if="entityData" class="flex flex-col gap-2 px-4 py-4">
            <template v-for="pair in scalarLabelPairs" :key="pair.key">
              <section v-if="shouldDisplayValue(entityData[pair.key])">
                <DetailRow
                  :label="pair.label"
                  :tooltip="pair.tooltip"
                  :variant="drawerVariant"
                >
                  <p class="result-value-small whitespace-pre-line">
                    {{ formatValue(entityData[pair.key]) }}
                  </p>
                </DetailRow>
              </section>
            </template>

            <section v-if="domesticInstrumentItems.length">
              <DetailRow label="Legal Provisions">
                <RelatedItemsList
                  :items="domesticInstrumentItems"
                  base-path="/domestic-instrument"
                />
              </DetailRow>
            </section>

            <template v-for="rel in relationSections" :key="rel.relationKey">
              <section v-if="rel.items.length > 0">
                <DetailRow :label="rel.label" :variant="rel.variant">
                  <RelatedItemsList
                    :items="rel.items"
                    :base-path="rel.basePath"
                  />
                </DetailRow>
              </section>
            </template>

            <section v-if="isJurisdiction && jurisdictionCode">
              <DetailRow label="Questions & Answers" variant="jurisdiction">
                <JurisdictionDrawerQA :jurisdiction-code="jurisdictionCode" />
              </DetailRow>
            </section>

            <section v-if="isQuestion && questionSuffix">
              <DetailRow label="" variant="question">
                <DrawerAnswerMap :question-suffix="questionSuffix" />
              </DetailRow>
            </section>
          </div>
        </div>
      </div>
    </template>
  </USlideover>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useQuery } from "@tanstack/vue-query";
import { useEntityDrawer } from "@/composables/useEntityDrawer";
import { getEntityConfig, mapRelationToItem } from "@/config/entityRegistry";
import type { RelationConfig } from "@/config/entityRegistry";
import { useApiClient } from "@/composables/useApiClient";
import type { RelatedItem } from "@/types/ui";
import DetailRow from "@/components/ui/DetailRow.vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import InlineError from "@/components/ui/InlineError.vue";
import JurisdictionDrawerQA from "@/components/jurisdiction/JurisdictionDrawerQA.vue";
import DrawerAnswerMap from "@/components/jurisdiction/DrawerAnswerMap.vue";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";

const route = useRoute();
const { isOpen, entity, closeDrawer, openDrawer } = useEntityDrawer();

const config = computed(() =>
  entity.value ? getEntityConfig(entity.value.basePath) : undefined,
);

const { client } = useApiClient();

const resolvedTable = computed(() => {
  if (!entity.value) return undefined;
  if (entity.value.table === "Answers" && !entity.value.coldId.includes("_")) {
    return "Questions" as const;
  }
  return entity.value.table;
});

const {
  data: rawData,
  isLoading,
  error: queryError,
} = useQuery({
  queryKey: computed(() => [
    "entity-drawer",
    resolvedTable.value,
    entity.value?.coldId,
  ]),
  queryFn: async () => {
    if (!entity.value || !config.value || !resolvedTable.value) return null;
    const { data, error } = await client.POST("/search/details", {
      body: { table: resolvedTable.value, id: entity.value.coldId },
    });
    if (error) throw error;
    return config.value.process(data);
  },
  enabled: computed(() => Boolean(entity.value?.coldId && resolvedTable.value)),
});

const entityData = computed(() => {
  if (!rawData.value) return null;
  return rawData.value as Record<string, unknown>;
});

const fullPagePath = computed(() => {
  if (!entity.value) return "/";
  const id = entity.value.coldId;
  const basePath = entity.value.basePath;
  return id.startsWith("/") ? id : `${basePath}/${id}`;
});

const hasDetailPage = computed(() => config.value?.hasDetailPage !== false);

const drawerVariant = computed(() => {
  if (!entity.value) return undefined;
  const variantMap: Record<string, string> = {
    "/court-decision": "court-decision",
    "/question": "question",
    "/literature": "literature",
    "/jurisdiction": "jurisdiction",
    "/specialist": "specialist",
    "/domestic-instrument": "instrument",
    "/regional-instrument": "instrument",
    "/international-instrument": "instrument",
    "/arbitral-rule": "arbitration",
    "/arbitral-award": "arbitration",
  };
  return variantMap[entity.value.basePath];
});

interface KeyLabelPair {
  key: string;
  label: string;
  tooltip?: string;
}

const scalarLabelPairs = computed<KeyLabelPair[]>(() => {
  if (!config.value) return [];
  const tooltips = config.value.tooltips ?? {};
  const skip = config.value.skipLabelKeys;
  return Object.entries(config.value.labels)
    .filter(([key]) => !skip.has(key))
    .map(([key, label]) => ({
      key,
      label,
      tooltip: tooltips[key],
    }));
});

interface RelationSection extends RelationConfig {
  items: RelatedItem[];
}

const relationSections = computed<RelationSection[]>(() => {
  if (!config.value || !entityData.value) return [];
  const relations = entityData.value.relations as
    | Record<string, Record<string, unknown>[]>
    | undefined;
  if (!relations) return [];

  return config.value.relations
    .map((rel) => {
      const items = (relations[rel.relationKey] ?? []).map(mapRelationToItem);
      return { ...rel, items };
    })
    .filter((rel) => rel.items.length > 0);
});

const domesticInstrumentItems = computed<RelatedItem[]>(() => {
  if (!entityData.value) return [];
  const relations = entityData.value.relations as
    | Record<string, Record<string, unknown>[]>
    | undefined;
  if (!relations?.domesticInstruments) return [];
  return relations.domesticInstruments.map(mapRelationToItem);
});

const pageJurisdictionCode = computed(() => {
  if (route.path.startsWith("/jurisdiction/")) {
    return route.params.coldId as string;
  }
  return undefined;
});

const firstJurisdiction = computed(() => {
  if (!entityData.value) return undefined;
  if (isJurisdiction.value) return undefined;
  const relations = entityData.value.relations as
    | Record<string, Record<string, unknown>[]>
    | undefined;
  const jurisdictions = relations?.jurisdictions;
  if (!jurisdictions?.length) return undefined;
  const j = jurisdictions[0]!;
  const code = (j.coldId as string) || "";
  const name = (j.name as string) || "";
  if (!code || !name) return undefined;
  if (code === pageJurisdictionCode.value) return undefined;
  return { code, name };
});

const headerJurisdiction = computed(() => firstJurisdiction.value?.name);

const headerJurisdictionCode = computed(
  () => firstJurisdiction.value?.code || "",
);

function handleJurisdictionClick(event: MouseEvent) {
  if (event.metaKey || event.ctrlKey) return;
  event.preventDefault();
  if (headerJurisdictionCode.value) {
    openDrawer(headerJurisdictionCode.value, "Jurisdictions", "/jurisdiction");
  }
}

const isJurisdiction = computed(
  () => entity.value?.basePath === "/jurisdiction",
);

const jurisdictionCode = computed(() => {
  if (!isJurisdiction.value || !entity.value) return undefined;
  return entity.value.coldId;
});

const isQuestion = computed(() => entity.value?.basePath === "/question");

const questionSuffix = computed(() => {
  if (!isQuestion.value || !entity.value) return undefined;
  const id = entity.value.coldId;
  const parts = id.split("_");
  if (parts.length > 1) return "_" + parts.slice(1).join("_");
  return "_" + id;
});

function shouldDisplayValue(value: unknown): boolean {
  if (!value) return false;
  if (value === "NA" || value === "N/A") return false;
  if (Array.isArray(value) && value.length === 0) return false;
  if (typeof value === "string" && value.trim() === "") return false;
  return true;
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "\u2014";
  if (Array.isArray(value)) {
    if (value.length === 0) return "\u2014";
    if (typeof value[0] === "string") return value.join(", ");
    return String(value.length) + " items";
  }
  return String(value);
}
</script>
