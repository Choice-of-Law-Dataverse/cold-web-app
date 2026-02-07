<template>
  <ContentPageLayout>
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";

const { data: page } = await useAsyncData("press", () =>
  queryCollection("content").path("/press").first(),
);
</script>
