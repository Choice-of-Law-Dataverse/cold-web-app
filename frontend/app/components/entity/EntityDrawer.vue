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
        <div class="flex items-center justify-between gap-3 px-6 py-5">
          <div class="flex min-w-0 items-center gap-2">
            <UButton
              v-if="canGoBack"
              icon="i-lucide-arrow-left"
              variant="ghost"
              color="neutral"
              size="xs"
              @click="goBack"
            />
            <CardTags
              :formatted-jurisdiction="headerJurisdictions"
              :legal-family="headerLegalFamily"
              :source-table-label="headerSourceTable"
              :label-color-class="headerLabelColor"
              :formatted-theme="[]"
            />
          </div>
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
          <InlineError v-else-if="error" :error="error" class="p-6" />
          <div
            v-else-if="entityData && config"
            class="flex flex-col gap-2 px-4 py-4"
          >
            <component
              v-if="customContentComponent"
              :is="customContentComponent"
              :data="entityData"
            />
            <EntityContent v-else :base-path="basePath!" :data="entityData" />

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
import { computed, type Component } from "vue";
import { useEntityDrawer } from "@/composables/useEntityDrawer";
import { useEntityData } from "@/composables/useEntityData";
import DetailRow from "@/components/ui/DetailRow.vue";
import EntityContent from "@/components/entity/EntityContent.vue";
import CourtDecisionContent from "@/components/entity/content/CourtDecisionContent.vue";
import LiteratureContent from "@/components/entity/content/LiteratureContent.vue";
import DomesticInstrumentContent from "@/components/entity/content/DomesticInstrumentContent.vue";
import SpecialistContent from "@/components/entity/content/SpecialistContent.vue";
import RegionalInstrumentContent from "@/components/entity/content/RegionalInstrumentContent.vue";
import InternationalInstrumentContent from "@/components/entity/content/InternationalInstrumentContent.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import InlineError from "@/components/ui/InlineError.vue";
import JurisdictionDrawerQA from "@/components/jurisdiction/JurisdictionDrawerQA.vue";
import DrawerAnswerMap from "@/components/jurisdiction/DrawerAnswerMap.vue";
import CardTags from "@/components/ui/CardTags.vue";

const contentComponents: Record<string, Component> = {
  CourtDecisionContent,
  LiteratureContent,
  DomesticInstrumentContent,
  SpecialistContent,
  RegionalInstrumentContent,
  InternationalInstrumentContent,
};

const route = useRoute();
const { isOpen, entity, canGoBack, closeDrawer, goBack } = useEntityDrawer();

const basePath = computed(() => entity.value?.basePath);
const coldId = computed(() => entity.value?.coldId ?? "");

const {
  data: entityData,
  isLoading,
  error,
  config,
} = useEntityData(basePath, coldId);

const customContentComponent = computed(() => {
  const id = config.value?.contentComponentId;
  return id ? contentComponents[id] : undefined;
});

const fullPagePath = computed(() => {
  if (!entity.value) return "/";
  const id = entity.value.coldId;
  const bp = entity.value.basePath;
  return id.startsWith("/") ? id : `${bp}/${id}`;
});

const hasDetailPage = computed(() => config.value?.hasDetailPage !== false);

const pageJurisdictionCode = computed(() => {
  if (route.path.startsWith("/jurisdiction/")) {
    return route.params.coldId as string;
  }
  return undefined;
});

const headerJurisdictions = computed<string[]>(() => {
  const data = entityData.value;
  if (!data || isJurisdiction.value) return [];
  if (!("relations" in data)) return [];
  const jurisdictions = data.relations.jurisdictions;
  if (!jurisdictions?.length) return [];
  const filtered = jurisdictions
    .filter((j) => j.coldId !== pageJurisdictionCode.value)
    .map((j) => j.name || "")
    .filter((name) => name);
  if (filtered.length !== 1) return [];
  return filtered;
});

const headerSourceTable = computed(() => config.value?.singularLabel ?? "");

const headerLabelColor = computed(() => {
  const variant = config.value?.variant;
  if (!variant) return "";
  if (variant === "jurisdiction") return "hidden";
  return `label-${variant}`;
});

const headerLegalFamily = computed<string[]>(() => {
  const data = entityData.value;
  if (!data || !("legalFamily" in data)) return [];
  const value = String(data.legalFamily || "");
  if (!value || value === "N/A") return [];
  return value
    .split(",")
    .map((f: string) => f.trim())
    .filter((f: string) => f);
});

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
</script>

<style scoped>
:deep(.tags-container) {
  white-space: normal;
  gap: 0.375rem 0;
}
</style>
