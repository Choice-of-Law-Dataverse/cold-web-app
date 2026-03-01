<template>
  <ResultCard :result-data="processedData ?? {}" card-type="Literature">
    <div class="flex flex-col gap-0">
      <DetailRow :label="getLabel('Title')">
        <div :class="fieldClasses('Title')">
          {{ getValue("Title") }}
          <span v-if="processedData?.['Open Access']"
            ><img
              class="ml-1 inline-flex w-3"
              src="https://choiceoflaw.blob.core.windows.net/assets/Open_Access_logo_PLoS_transparent.svg"
              alt="Open Access Logo"
          /></span>
        </div>
      </DetailRow>

      <DetailRow :label="getLabel('Author')">
        <div :class="fieldClasses('Author')">
          {{ getValue("Author") }}
        </div>
      </DetailRow>

      <DetailRow :label="getLabel('Publication Year')">
        <div :class="fieldClasses('Publication Year')">
          {{ getValue("Publication Year") }}
        </div>
      </DetailRow>

      <template
        v-if="
          shouldDisplay('Publication Title') &&
          processedData?.['Publication Title']
        "
      >
        <DetailRow :label="getLabel('Publication Title')">
          <div :class="fieldClasses('Publication Title')">
            {{ getValue("Publication Title") }}
          </div>
        </DetailRow>
      </template>

      <template
        v-else-if="shouldDisplay('Publisher') && processedData?.['Publisher']"
      >
        <DetailRow :label="getLabel('Publisher')">
          <div :class="fieldClasses('Publisher')">
            {{ getValue("Publisher") }}
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
