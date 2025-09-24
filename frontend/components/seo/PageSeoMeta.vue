<template>
  <div style="display: none;">
    <!-- This component only handles SEO meta tags, no visible content -->
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useSeoMeta, useHead, useRoute } from '#imports';

interface Props {
  titleCandidates: (string | null | undefined)[];
  fallback: string;
}

const props = defineProps<Props>();
const route = useRoute();

/**
 * Generate consistent page title from candidates and fallback
 */
const pageTitle = computed(() => {
  // Filter out null/undefined/empty values and trim whitespace
  const validParts = props.titleCandidates
    .filter((part): part is string => Boolean(part?.trim()))
    .map(part => part.trim());

  // If we have valid parts, join them with the fallback and "CoLD"
  if (validParts.length > 0) {
    return [...validParts, props.fallback, "CoLD"].join(" — ");
  }

  // Otherwise use just the fallback and "CoLD"
  return [props.fallback, "CoLD"].join(" — ");
});

// Handle SEO meta tags
useSeoMeta({
  title: pageTitle,
  description: pageTitle,
  ogTitle: pageTitle,
  ogDescription: pageTitle,
  twitterTitle: pageTitle,
  twitterDescription: pageTitle,
});

// Handle canonical URL
useHead({
  link: [
    {
      rel: "canonical",
      href: `https://cold.global${route.fullPath}`,
    },
  ],
});
</script>