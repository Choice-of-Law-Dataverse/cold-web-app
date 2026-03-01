<template>
  <LandingCardShell
    title="Top Literature Themes"
    subtitle="Browse essential legal publications"
    header-class="text-left md:whitespace-nowrap"
  >
    <UButton
      v-for="(suggestion, index) in searchSuggestions"
      :key="index"
      variant="soft"
      color="neutral"
      class="type-literature"
      @click="handleSuggestionClick(suggestion)"
    >
      <Icon name="i-material-symbols:book-outline" class="item-icon" />
      <span class="text-left break-words">{{ suggestion }}</span>
    </UButton>
  </LandingCardShell>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { ref } from "vue";
import LandingCardShell from "@/components/landing-page/LandingCardShell.vue";

const router = useRouter();

const searchSuggestions = ref([
  "Arbitration",
  "Rules of law",
  "Overriding mandatory rules",
]);

function handleSuggestionClick(suggestion: string) {
  router.push({
    name: "search",
    query: { theme: suggestion, type: "Literature" },
  });
}
</script>
