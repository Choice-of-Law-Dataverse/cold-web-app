<template>
  <ResultCard :result-data="processedData ?? {}" card-type="Literature">
    <div class="flex flex-col gap-0">
      <DetailRow :label="getLabel('title')">
        <div :class="fieldClasses('title')">
          {{ getValue("title") }}
          <span v-if="processedData?.openAccess"
            ><img
              class="ml-1 inline-flex w-3"
              src="https://choiceoflaw.blob.core.windows.net/assets/Open_Access_logo_PLoS_transparent.svg"
              alt="Open Access Logo"
          /></span>
        </div>
      </DetailRow>

      <DetailRow :label="getLabel('author')">
        <div :class="fieldClasses('author')">
          {{ getValue("author") }}
        </div>
      </DetailRow>

      <DetailRow :label="getLabel('publicationYear')">
        <div :class="fieldClasses('publicationYear')">
          {{ getValue("publicationYear") }}
        </div>
      </DetailRow>

      <template
        v-if="
          shouldDisplay('publicationTitle') && processedData?.publicationTitle
        "
      >
        <DetailRow :label="getLabel('publicationTitle')">
          <div :class="fieldClasses('publicationTitle')">
            {{ getValue("publicationTitle") }}
          </div>
        </DetailRow>
      </template>

      <template
        v-else-if="shouldDisplay('publisher') && processedData?.publisher"
      >
        <DetailRow :label="getLabel('publisher')">
          <div :class="fieldClasses('publisher')">
            {{ getValue("publisher") }}
          </div>
        </DetailRow>
      </template>
    </div>
  </ResultCard>
</template>

<script setup lang="ts">
import ResultCard from "@/components/search-results/ResultCard.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import { literatureCardConfig } from "@/config/cardConfigs";
import { useCardFields } from "@/composables/useCardFields";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const { getLabel, getValue, shouldDisplay, fieldClasses, processedData } =
  useCardFields(literatureCardConfig, props.resultData);
</script>
