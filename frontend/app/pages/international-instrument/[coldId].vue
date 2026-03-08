<template>
  <div>
    <h1 v-if="internationalInstrument?.name" class="sr-only">
      {{ internationalInstrument.name }}
    </h1>
    <BaseDetailLayout
      table="International Instruments"
      :loading="loading"
      :error="error"
      :data="internationalInstrument || {}"
      :field-order="entityConfig.fieldOrder"
      :label-overrides="entityConfig.labelOverrides"
      :tooltips="entityConfig.tooltips"
      :relations="internationalInstrument?.relations"
      :show-suggest-edit="true"
    >
      <template #name="{ value, label }">
        <DetailRow :label="label">
          <TitleWithActions>
            {{ value }}
            <template #actions>
              <PdfLink
                :pdf-field="internationalInstrument?.attachment"
                :record-id="instrumentId"
                folder-name="international-instruments"
              />
              <SourceExternalLink
                :source-url="internationalInstrument?.displayUrl"
              />
            </template>
          </TitleWithActions>
        </DetailRow>
      </template>

      <template #footer>
        <LastModified :date="internationalInstrument?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[internationalInstrument?.name]"
      fallback="International Instrument"
    />

    <EntityFeedback
      entity-type="international_instrument"
      :entity-id="instrumentId"
      :entity-title="(internationalInstrument?.name as string) || undefined"
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
import { useInternationalInstrument } from "@/composables/useRecordDetails";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { getEntityConfig } from "@/config/entityRegistry";

const entityConfig = getEntityConfig("/international-instrument")!;

const route = useRoute();
const instrumentId = ref(route.params.coldId as string);

const {
  data: internationalInstrument,
  isLoading: loading,
  error,
} = useInternationalInstrument(instrumentId);
</script>
