<template>
  <ContentPageLayout>
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";

useHead({
  title: "Endorsements — CoLD",
});

const { data: page } = await useAsyncData("endorsements", () =>
  queryCollection("content").path("/endorsements").first(),
);
</script>
