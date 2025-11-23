<template>
  <div style="display: none" />
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useSeoMeta, useHead, useRoute } from "#imports";

interface Props {
  titleCandidates: (string | null | undefined)[];
  fallback: string;
}

const props = defineProps<Props>();
const route = useRoute();

const pageTitle = computed(() => {
  const validParts = props.titleCandidates
    .filter((part): part is string => Boolean(part?.trim()))
    .map((part) => part.trim());

  if (validParts.length > 0) {
    return [...validParts, props.fallback, "CoLD"].join(" — ");
  }

  return [props.fallback, "CoLD"].join(" — ");
});

useSeoMeta({
  title: pageTitle,
  description: pageTitle,
  ogTitle: pageTitle,
  ogDescription: pageTitle,
  twitterTitle: pageTitle,
  twitterDescription: pageTitle,
});

useHead({
  link: [
    {
      rel: "canonical",
      href: `https://cold.global${route.fullPath}`,
    },
  ],
});
</script>
