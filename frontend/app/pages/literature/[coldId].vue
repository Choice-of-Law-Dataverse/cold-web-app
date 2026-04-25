<template>
  <div>
    <h1 v-if="data?.title" class="sr-only">
      {{ data.title }}
    </h1>
    <BaseDetailLayout
      table="Literature"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
    >
      <template #title-actions>
        <template v-if="data">
          <PdfLink
            :pdf-field="undefined"
            :record-id="String(data.coldId || '')"
            folder-name="literatures"
          />
          <SourceExternalLink
            :source-url="String(data.openAccessUrl || data.url || '')"
            :label="data.openAccessUrl ? 'Open Access Link' : 'Link'"
            :open-access="!!data.openAccessUrl"
          />
        </template>
      </template>

      <LiteratureContent v-if="data" :data="data" />

      <template #footer>
        <LastModified :date="data?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta :title-candidates="[data?.title]" fallback="Literature" />

    <EntityFeedback
      entity-type="literature"
      :entity-id="coldId"
      :entity-title="data?.title ?? undefined"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import LiteratureContent from "@/components/entity/content/LiteratureContent.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();

const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/literature", coldId);
</script>
