<template>
  <div>
    <h1 v-if="regionalInstrument?.abbreviation" class="sr-only">
      {{ regionalInstrument.abbreviation }}
    </h1>
    <BaseDetailLayout
      table="Regional Instruments"
      :loading="loading"
      :error="error"
      :data="regionalInstrument || {}"
      :field-order="entityConfig.fieldOrder"
      :label-overrides="entityConfig.labelOverrides"
      :tooltips="entityConfig.tooltips"
      :relations="regionalInstrument?.relations"
      :show-suggest-edit="true"
    >
      <template #abbreviation="{ value, label }">
        <DetailRow :label="label">
          <TitleWithActions>
            {{ value }}
            <template #actions>
              <PdfLink
                :pdf-field="regionalInstrument?.attachment"
                :record-id="route.params.coldId as string"
                folder-name="regional-instruments"
              />
              <SourceExternalLink :source-url="regionalInstrument?.url" />
            </template>
          </TitleWithActions>
        </DetailRow>
      </template>

      <template #footer>
        <LastModified :date="regionalInstrument?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[regionalInstrument?.abbreviation]"
      fallback="Regional Instrument"
    />

    <EntityFeedback
      entity-type="regional_instrument"
      :entity-id="instrumentId"
      :entity-title="(regionalInstrument?.abbreviation as string) || undefined"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import TitleWithActions from "@/components/ui/TitleWithActions.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { useRegionalInstrument } from "@/composables/useRecordDetails";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { getEntityConfig } from "@/config/entityRegistry";

const entityConfig = getEntityConfig("/regional-instrument")!;

const route = useRoute();
const instrumentId = ref(route.params.coldId as string);

const {
  data: regionalInstrument,
  isLoading: loading,
  error,
} = useRegionalInstrument(instrumentId);
</script>
