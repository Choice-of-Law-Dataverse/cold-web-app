<script lang="ts" setup>
import { learnNavLinks } from "@/config/pageConfigs.js";
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";

const route = useRoute();
const router = useRouter();

onMounted(() => {
  if (route.path === "/learn") {
    router.replace("/learn/open-educational-resources");
  }
});

const { data: page } = await useAsyncData(route.path, () => {
  return queryCollection("content").path(route.path).first();
});
</script>

<template>
  <ContentPageLayout
    :nav-links="learnNavLinks"
    :enable-hierarchical-numbering="true"
  >
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>
