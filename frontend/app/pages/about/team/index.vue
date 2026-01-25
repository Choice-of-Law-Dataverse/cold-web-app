<template>
  <ContentPageLayout>
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";

const { data: page } = await useAsyncData("team", () =>
  queryCollection("content").path("/team").first(),
);
</script>
