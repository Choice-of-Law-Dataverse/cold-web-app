<template>
  <ContentPageLayout page-heading="About the Choice of Law Dataverse">
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import { onMounted, nextTick } from "vue";
import { useRoute } from "vue-router";
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";

useSeoMeta({
  title: "About CoLD — CoLD",
  description:
    "The Choice of Law Dataverse is an open research project mapping how jurisdictions worldwide treat party autonomy in international commercial contracts.",
  ogTitle: "About CoLD — CoLD",
  ogDescription:
    "The Choice of Law Dataverse is an open research project mapping how jurisdictions worldwide treat party autonomy in international commercial contracts.",
});

const { data: page } = await useAsyncData("about_cold", () =>
  queryCollection("content").path("/about_cold").first(),
);

onMounted(async () => {
  const route = useRoute();
  if (route.hash) {
    await nextTick();
    const el = document.querySelector(route.hash);
    if (el) {
      el.scrollIntoView({ behavior: "auto" });
    }
  }
});
</script>
