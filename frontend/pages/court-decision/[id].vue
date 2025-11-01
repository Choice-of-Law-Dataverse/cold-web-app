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
            :section-label="
              keyLabelLookup.get('Domestic Legal Provisions')?.label
            "
            :section-tooltip="
              keyLabelLookup.get('Domestic Legal Provisions')?.tooltip
            "
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
            class="flex flex-col md:w-full md:flex-row md:items-start md:gap-6"
          >
            <!-- Label column -->
            <div class="label label-key mt-0 md:w-48 md:flex-shrink-0">
              <span class="flex items-center">
                Quote
                <InfoPopover
                  v-if="keyLabelLookup.get('Quote')?.tooltip"
                  :text="keyLabelLookup.get('Quote')?.tooltip"
                />
              </span>
            </div>
            <!-- Content column -->
            <div class="md:flex-1">
              <div
                v-if="
                  (courtDecision as Record<string, unknown>)
                    .hasEnglishQuoteTranslation &&
                  (courtDecision as Record<string, unknown>)['Quote'] &&
                  (
                    (courtDecision as Record<string, unknown>)[
                      'Quote'
                    ] as string
                  )?.trim() !== ''
                "
                class="mb-2 flex items-center gap-1"
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
              <div>
                <p class="prose mt-0 whitespace-pre-line">
                  {{
                    showEnglishQuote &&
                    (courtDecision as any).hasEnglishQuoteTranslation &&
                    (courtDecision as any)["Quote"] &&
                    (courtDecision as any)["Quote"]?.trim() !== ""
                      ? (courtDecision as any)["Translated Excerpt"]
                      : (courtDecision as any)["Quote"] ||
                        (courtDecision as any)["Translated Excerpt"]
                  }}
                </p>
              </div>
            </div>
          </div>
        </section>
      </template>
      <!-- Custom rendering for Related Questions section -->
      <template #related-questions>
        <section class="section-gap m-0 p-0">
          <RelatedQuestions
            :jurisdiction-code="
              ((courtDecision as Record<string, unknown>)?.[
                'Jurisdictions Alpha-3 Code'
              ] as string) || ''
            "
            :questions="
              ((courtDecision as Record<string, unknown>)?.[
                'Questions'
              ] as string) || ''
            "
            :tooltip="keyLabelLookup.get('Related Questions')?.tooltip"
          />
        </section>
      </template>
      <template #related-literature>
        <section class="section-gap m-0 p-0">
          <div class="flex flex-col md:w-full md:flex-row md:items-start md:gap-6">
            <!-- Label column -->
            <div class="label label-key mt-0 md:w-48 md:flex-shrink-0">
              <span class="flex items-center">
                Related Literature
                <InfoPopover
                  v-if="keyLabelLookup.get('Related Literature')?.tooltip"
                  :text="keyLabelLookup.get('Related Literature')?.tooltip"
                />
              </span>
            </div>
            <!-- Content column -->
            <div class="md:flex-1">
              <RelatedLiterature
                :themes="
                  ((courtDecision as Record<string, unknown>)?.themes as string) ||
                  ''
                "
                :value-class-map="valueClassMap['Related Literature']"
                :use-id="false"
                :show-label="false"
              />
            </div>
          </div>
        </section>
      </template>

      <!-- Custom rendering for Full Text (Original Text) section -->
      <template #original-text="{ value }">
        <section
          v-if="value && value.trim() !== ''"
          class="section-gap m-0 p-0"
        >
          <div class="flex flex-col md:w-full md:flex-row md:items-start md:gap-6">
            <!-- Label column -->
            <h4 class="label label-key mt-0 md:w-48 md:flex-shrink-0">
              <span class="flex items-center">
                {{ keyLabelLookup.get("Original Text")?.label || "Full Text" }}
              </span>
            </h4>
            <!-- Content column -->
            <div class="md:flex-1">
              <div :class="valueClassMap['Original Text']">
                <div v-if="!showFullText && value.length > 400">
                  <p class="prose mt-0">
                    {{ value.slice(0, 400) }}<span v-if="value.length > 400">…</span>
                  </p>
                  <NuxtLink
                    class="ml-2 cursor-pointer"
                    @click="showFullText = true"
                  >
                    <Icon name="material-symbols:add" :class="iconClass" />
                    Show more
                  </NuxtLink>
                </div>
                <div v-else>
                  <p class="prose mt-0">
                    {{ value }}
                  </p>
                  <NuxtLink
                    v-if="value.length > 400"
                    class="ml-2 cursor-pointer"
                    @click="showFullText = false"
                  >
                    <Icon name="material-symbols:remove" :class="iconClass" />
                    Show less
                  </NuxtLink>
                </div>
              </div>
            </div>
          </div>
        </section>
      </template>
    </BaseDetailLayout>

    <!-- Error Alert -->
    <UAlert v-if="error" type="error" class="mx-auto mt-4 max-w-container">
      {{ error }}
    </UAlert>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[
        ((courtDecision as Record<string, unknown>)?.[
          'Case Title'
        ] as string) !== 'Not found'
          ? ((courtDecision as Record<string, unknown>)?.[
              'Case Title'
            ] as string)
          : null,
        (courtDecision as Record<string, unknown>)?.['Case Citation'] as string,
      ]"
      fallback="Court Decision"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import RelatedLiterature from "@/components/literature/RelatedLiterature.vue";
import RelatedQuestions from "@/components/legal/RelatedQuestions.vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";
import ProvisionRenderer from "@/components/legal/SectionRenderer.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useCourtDecision } from "@/composables/useCourtDecision";
import { useDetailDisplay } from "@/composables/useDetailDisplay";
import { courtDecisionConfig } from "@/config/pageConfigs";

defineProps({
  iconClass: {
    type: String,
    default: "text-base translate-y-[3px] mt-2 ml-[-12px]",
  },
});

const route = useRoute();

const {
  data: courtDecision,
  isLoading,
  error,
} = useCourtDecision(computed(() => route.params.id as string));

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  courtDecision,
  courtDecisionConfig,
);

const showEnglishQuote = ref(true);

// For Full Text show more/less
const showFullText = ref(false);

const keyLabelLookup = computed(() => {
  const map = new Map();
  courtDecisionConfig.keyLabelPairs.forEach((pair) => {
    map.set(pair.key, pair);
  });
  return map;
});
</script>
