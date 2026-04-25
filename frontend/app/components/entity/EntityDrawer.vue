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
      <div class="flex h-full flex-col overflow-hidden">
        <header class="drawer-header rounded-tl-xl">
          <div class="drawer-header__top">
            <UButton
              v-if="canGoBack"
              icon="i-lucide-arrow-left"
              variant="ghost"
              color="neutral"
              size="md"
              class="drawer-header__icon-btn"
              @click="goBack"
            />
            <span v-else class="drawer-header__spacer" aria-hidden="true" />
            <div class="drawer-header__actions">
              <UButton
                v-if="hasDetailPage"
                :to="fullPagePath"
                leading-icon="i-lucide-maximize"
                trailing-icon="i-lucide-arrow-up-right"
                color="primary"
                variant="ghost"
                size="xs"
                class="drawer-header__fullpage"
                @click="closeDrawer"
              >
                Full page
              </UButton>
              <UButton
                icon="i-lucide-x"
                variant="ghost"
                color="neutral"
                size="md"
                aria-label="Close"
                class="drawer-header__icon-btn"
                @click="closeDrawer"
              />
            </div>
          </div>

          <MetaBand
            v-if="entityData"
            :result-data="entityData"
            :card-type="headerSourceTable"
            :formatted-jurisdiction="headerJurisdictions"
            :legal-family="headerLegalFamily"
            :show-cite="false"
            :show-json="false"
            :show-print="false"
            compact
          />
        </header>

        <div class="drawer-header__rule" />

        <div class="flex-1 overflow-x-hidden overflow-y-auto">
          <div v-if="isLoading" class="p-6">
            <LoadingBar />
          </div>
          <InlineError v-else-if="error" :error="error" class="p-6" />
          <div
            v-else-if="entityData && config"
            class="flex flex-col gap-4 px-5 py-5"
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
import { computed, watch, type Component } from "vue";
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
import QuestionContent from "@/components/entity/content/QuestionContent.vue";
import JurisdictionContent from "@/components/entity/content/JurisdictionContent.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import InlineError from "@/components/ui/InlineError.vue";
import JurisdictionDrawerQA from "@/components/jurisdiction/JurisdictionDrawerQA.vue";
import DrawerAnswerMap from "@/components/jurisdiction/DrawerAnswerMap.vue";
import MetaBand from "@/components/ui/MetaBand.vue";
import { primaryJurisdictionAlpha3 } from "@/utils/jurisdictionParser";

const contentComponents: Record<string, Component> = {
  CourtDecisionContent,
  LiteratureContent,
  DomesticInstrumentContent,
  SpecialistContent,
  RegionalInstrumentContent,
  InternationalInstrumentContent,
  QuestionContent,
  JurisdictionContent,
};

const route = useRoute();
const { isOpen, entity, canGoBack, closeDrawer, goBack } = useEntityDrawer();

watch(
  () => route.fullPath,
  () => closeDrawer(),
);

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
  const filtered = jurisdictions.filter(
    (j) => j.coldId !== pageJurisdictionCode.value,
  );
  if (filtered.length === 1) {
    const name = filtered[0]?.name;
    return name ? [name] : [];
  }
  const primary = primaryJurisdictionAlpha3(
    data as Record<string, unknown>,
  ).toUpperCase();
  if (!primary) return [];
  const match = filtered.find((j) => j.coldId?.toUpperCase() === primary);
  return match?.name ? [match.name] : [];
});

const headerSourceTable = computed(() => config.value?.singularLabel ?? "");

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
.drawer-header {
  position: relative;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--color-cold-purple) 5%, white) 0%,
    color-mix(in srgb, var(--color-cold-purple) 2%, white) 60%,
    color-mix(in srgb, var(--color-cold-green) 1.5%, white) 100%
  );
}

.drawer-header__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.375rem 0.625rem 0.375rem 0.625rem;
  min-height: 2.25rem;
}

.drawer-header__spacer {
  display: block;
  width: 1px;
  height: 1px;
}

.drawer-header__actions {
  display: flex;
  align-items: center;
  gap: 0.125rem;
}

:deep(.drawer-header__icon-btn) {
  color: color-mix(in srgb, var(--color-cold-night) 55%, transparent);
  transition:
    color 0.15s ease,
    background 0.15s ease;
}

:deep(.drawer-header__icon-btn:hover) {
  color: var(--color-cold-night);
  background: color-mix(in srgb, var(--color-cold-night) 6%, transparent);
}

:deep(.drawer-header__fullpage) {
  font-weight: 500;
  letter-spacing: -0.005em;
  padding-inline: 0.5rem;
  background: transparent;
  transition:
    background 0.15s ease,
    color 0.15s ease;
}

:deep(.drawer-header__fullpage:hover) {
  background: color-mix(in srgb, var(--color-cold-purple) 8%, transparent);
}

:deep(.drawer-header__fullpage [class*="trailing"]) {
  font-size: 0.85em;
  margin-left: 0.0625rem;
  transition: transform 0.18s ease;
}

:deep(.drawer-header__fullpage:hover [class*="trailing"]) {
  transform: translate(1px, -1px);
}

.drawer-header__rule {
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    color-mix(in srgb, var(--color-cold-purple) 35%, transparent) 18%,
    color-mix(in srgb, var(--color-cold-green) 30%, transparent) 82%,
    transparent 100%
  );
  flex-shrink: 0;
}
</style>
