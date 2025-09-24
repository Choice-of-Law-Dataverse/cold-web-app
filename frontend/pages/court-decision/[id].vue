<template>
  <div>
    <BaseDetailLayout
      :loading="isLoading"
      :result-data="courtDecision || {}"
      :key-label-pairs="computedKeyLabelPairs"
      :value-class-map="valueClassMap"
      :show-suggest-edit="true"
      source-table="Court Decisions"
    >
      <!-- Slot for Domestic Legal Provisions -->
      <template #domestic-legal-provisions="{ value }">
        <div :class="valueClassMap['Domestic Legal Provisions']">
          <ProvisionRenderer
            v-if="value"
            :id="value"
            section="Domestic Legal Provisions"
            :section-label="keyLabelLookup.get('Domestic Legal Provisions')?.label"
            :section-tooltip="keyLabelLookup.get('Domestic Legal Provisions')?.tooltip"
            table="Domestic Instruments"
            class="mb-8"
          />
        </div>
      </template>
      <!-- Custom rendering for Quote section -->
      <template #quote>
        <section class="section-gap m-0 p-0">
          <div
            v-if="
              courtDecision &&
              (courtDecision['Quote'] || courtDecision['Translated Excerpt'])
            "
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <span class="label flex flex-row items-center">Quote</span>
                <InfoPopover
                  v-if="keyLabelLookup.get('Quote')?.tooltip"
                  :text="keyLabelLookup.get('Quote')?.tooltip"
                  class="ml-[-8px]"
                />
              </div>
              <div
                v-if="
                  (courtDecision as Record<string, unknown>).hasEnglishQuoteTranslation &&
                  (courtDecision as Record<string, unknown>)['Quote'] &&
                  ((courtDecision as Record<string, unknown>)['Quote'] as string)?.trim() !== ''
                "
                class="flex items-center gap-1"
              >
                <span
                  class="label-key-provision-toggle mr-[-0px]"
                  :class="{
                    'opacity-25': showEnglishQuote,
                    'opacity-100': !showEnglishQuote,
                  }"
                >
                  Original
                </span>
                <UToggle
                  v-model="showEnglishQuote"
                  size="2xs"
                  class="bg-[var(--color-cold-gray)]"
                />
                <span
                  class="label-key-provision-toggle"
                  :class="{
                    'opacity-25': !showEnglishQuote,
                    'opacity-100': showEnglishQuote,
                  }"
                >
                  English
                </span>
              </div>
            </div>
            <div>
              <span class="whitespace-pre-line">
                {{
                  showEnglishQuote &&
                  (courtDecision as any).hasEnglishQuoteTranslation &&
                  (courtDecision as any)["Quote"] &&
                  (courtDecision as any)["Quote"]?.trim() !== ""
                    ? (courtDecision as any)["Translated Excerpt"]
                    : (courtDecision as any)["Quote"] ||
                      (courtDecision as any)["Translated Excerpt"]
                }}
              </span>
            </div>
          </div>
        </section>
      </template>
      <!-- Custom rendering for Related Questions section -->
      <template #related-questions>
        <section class="section-gap m-0 p-0">
          <RelatedQuestions
            :jurisdiction-code="
              (courtDecision as Record<string, unknown>)?.['Jurisdictions Alpha-3 Code'] as string || ''
            "
            :questions="(courtDecision as Record<string, unknown>)?.['Questions'] as string || ''"
            :tooltip="
              computedKeyLabelPairs.find(
                (pair) => pair.key === 'Related Questions',
              )?.tooltip
            "
          />
        </section>
      </template>
      <template #related-literature>
        <section class="section-gap m-0 p-0">
          <RelatedLiterature
            :themes="(courtDecision as Record<string, unknown>)?.themes as string || ''"
            :value-class-map="valueClassMap['Related Literature']"
            :use-id="false"
            :tooltip="keyLabelLookup.get('Related Literature')?.tooltip"
          />
        </section>
      </template>

      <!-- Custom rendering for Full Text (Original Text) section -->
      <template #original-text="{ value }">
        <section
          v-if="value && value.trim() !== ''"
          class="section-gap m-0 p-0"
        >
          <div class="mb-2 mt-12 flex items-center">
            <span class="label">
              {{ keyLabelLookup.get("Original Text")?.label || "Full Text" }}
            </span>
          </div>
          <div :class="valueClassMap['Original Text']">
            <span v-if="!showFullText && value.length > 400">
              {{ value.slice(0, 400) }}<span v-if="value.length > 400">…</span>
              <div>
                <NuxtLink
                  class="ml-2 cursor-pointer"
                  @click="showFullText = true"
                >
                  <Icon name="material-symbols:add" :class="iconClass" />
                  Show entire full text
                </NuxtLink>
              </div>
            </span>
            <span v-else>
              {{ value }}
              <div>
                <NuxtLink
                  v-if="value.length > 400"
                  class="ml-2 cursor-pointer"
                  @click="showFullText = false"
                >
                  <Icon name="material-symbols:remove" :class="iconClass" />
                  Show less
                </NuxtLink>
              </div>
            </span>
            <div>
              <a
                class="ml-2"
                :href="downloadPDFLink"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Icon
                  name="i-material-symbols:arrow-circle-down-outline"
                  :class="iconClass"
                />
                <span class="ml-1">Download the case as a PDF</span>
              </a>
            </div>
          </div>
        </section>
      </template>
    </BaseDetailLayout>

    <!-- Error Alert -->
    <UAlert v-if="error" type="error" class="mx-auto mt-4 max-w-container">
      {{ error }}
    </UAlert>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import RelatedLiterature from "@/components/literature/RelatedLiterature.vue";
import RelatedQuestions from "@/components/legal/RelatedQuestions.vue";
import InfoPopover from "~/components/ui/InfoPopover.vue";
import ProvisionRenderer from "@/components/legal/SectionRenderer.vue";
import { useCourtDecision } from "@/composables/useCourtDecision";
import { useDetailDisplay } from "@/composables/useDetailDisplay";
import { courtDecisionConfig } from "@/config/pageConfigs";
import { useSeoMeta } from "#imports";

defineProps({
  iconClass: {
    type: String,
    default: "text-base translate-y-[3px] mt-2 ml-[-12px]",
  },
});

const route = useRoute();

const { data: courtDecision, isLoading, error } = useCourtDecision(
  computed(() => route.params.id as string),
);

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  courtDecision,
  courtDecisionConfig,
);

const showEnglishQuote = ref(true);

// For Full Text show more/less
const showFullText = ref(false);

// Create lookup map for keyLabelPairs to avoid repetitive find operations
const keyLabelLookup = computed(() => {
  const map = new Map();
  courtDecisionConfig.keyLabelPairs.forEach(pair => {
    map.set(pair.key, pair);
  });
  return map;
});

// PDF download link logic (same as BaseCardHeader.vue)
const downloadPDFLink = computed(() => {
  const segments = route.path.split("/").filter(Boolean);
  const contentType = segments[0] || "unknown";
  const id = segments[1] || "";
  const folder = `${contentType}s`;
  return `https://choiceoflaw.blob.core.windows.net/${folder}/${id}.pdf`;
});

// Simplify page title generation with computed property
const pageTitle = computed(() => {
  if (!courtDecision.value) return "Court Decision — CoLD";
  const data = courtDecision.value as Record<string, unknown>;
  const caseTitle = data["Case Title"] as string;
  const citation = data["Case Citation"] as string;
  
  if (caseTitle?.trim() && caseTitle !== "Not found") {
    return `${caseTitle} — CoLD`;
  } else if (citation?.trim()) {
    return `${citation} — CoLD`;
  }
  return "Court Decision — CoLD";
});

// Use useSeoMeta for better performance
useSeoMeta({
  title: pageTitle,
  description: pageTitle,
  ogTitle: pageTitle,
  ogDescription: pageTitle,
  twitterTitle: pageTitle,
  twitterDescription: pageTitle,
});

// Canonical URL
useHead({
  link: [
    {
      rel: "canonical",
      href: `https://cold.global${route.fullPath}`,
    },
  ],
});
</script>
