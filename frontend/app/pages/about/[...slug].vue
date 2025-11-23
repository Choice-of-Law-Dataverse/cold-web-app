<script lang="ts" setup>
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";

const route = useRoute();
const router = useRouter();

onMounted(() => {
  if (route.path === "/about") {
    router.replace("/about/about-cold");
  }
});

const { data: page } = await useAsyncData(route.path, () => {
  return queryCollection("content").path(route.path).first();
});
</script>

<template>
  <ContentPageLayout>
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>
