<template>
  <EntityContent base-path="/court-decision" :data="data">
    <template #quote="{ label, tooltip }">
      <DetailRow
        v-if="data.quote || data.translatedExcerpt"
        :label="label"
        :tooltip="tooltip"
      >
        <div>
          <div
            v-if="
              data.hasEnglishQuoteTranslation &&
              data.quote &&
              String(data.quote).trim() !== ''
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
            <USwitch
              v-model="showEnglishQuote"
              size="sm"
              checked-icon="i-material-symbols-translate"
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
          <p class="result-value-small whitespace-pre-line">
            {{
              showEnglishQuote &&
              data.hasEnglishQuoteTranslation &&
              data.quote &&
              String(data.quote).trim() !== ""
                ? data.translatedExcerpt
                : data.quote || data.translatedExcerpt
            }}
          </p>
        </div>
      </DetailRow>
    </template>

    <template #originalText="{ value, label }">
      <DetailRow v-if="value && String(value).trim() !== ''" :label="label">
        <div>
          <p class="result-value-small">
            {{
              showFullText || String(value).length <= 400
                ? value
                : String(value).slice(0, 400) + "…"
            }}
          </p>
          <ShowMoreLess
            v-if="String(value).length > 400"
            v-model:is-expanded="showFullText"
          />
        </div>
      </DetailRow>
    </template>
  </EntityContent>
</template>

<script setup lang="ts">
import { ref } from "vue";
import EntityContent from "@/components/entity/EntityContent.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import ShowMoreLess from "@/components/ui/ShowMoreLess.vue";
import type { CourtDecision } from "@/types/entities/court-decision";

defineProps<{
  data: CourtDecision;
}>();

const showEnglishQuote = ref(true);
const showFullText = ref(false);
</script>
