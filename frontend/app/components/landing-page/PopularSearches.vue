<template>
  <LandingCardShell
    title="Popular Searches"
    subtitle="Start with frequent queries"
    header-class="text-left"
  >
    <UButton
      v-for="(item, index) in searchSuggestions"
      :key="index"
      variant="soft"
      color="neutral"
      @click="handleSuggestionClick(item.query)"
    >
      <Icon name="i-material-symbols:search" class="item-icon" />
      <span class="flex-1 text-left break-words">{{ item.query }}</span>
      <span class="result-count">{{ item.count }}+</span>
    </UButton>
  </LandingCardShell>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { ref } from "vue";
import LandingCardShell from "@/components/landing-page/LandingCardShell.vue";
import eventBus from "@/eventBus";

const router = useRouter();

const searchSuggestions = ref([
  { query: "Tacit Choice in Argentina", count: 15 },
  { query: "Party Autonomy in Switzerland", count: 42 },
  { query: "Public Policy in India", count: 28 },
]);

function handleSuggestionClick(suggestion: string) {
  eventBus.emit("update-search", suggestion);

  router.push({
    name: "search",
    query: { q: suggestion },
  });
}
</script>

<style scoped>
.result-count {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-cold-purple);
  background: color-mix(in srgb, var(--color-cold-purple) 10%, transparent);
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  white-space: nowrap;
}
</style>
