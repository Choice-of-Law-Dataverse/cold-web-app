<template>
  <ContentPageLayout>
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import { onMounted, nextTick } from "vue";
import { useRoute } from "vue-router";
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";

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
