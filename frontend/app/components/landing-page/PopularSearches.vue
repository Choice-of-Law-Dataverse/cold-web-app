<template>
  <UCard class="h-full w-full" :ui="{ body: '!p-0' }">
    <div class="gradient-top-border" />
    <div class="flex flex-col gap-4 p-4 sm:p-6">
      <div>
        <h2 class="card-title text-left">Popular Searches</h2>
        <p class="card-subtitle">Start with frequent queries</p>
      </div>

      <div class="flex w-full flex-col gap-2">
        <button
          v-for="(item, index) in searchSuggestions"
          :key="index"
          class="landing-item-button w-full"
          @click="handleSuggestionClick(item.query)"
        >
          <Icon name="i-material-symbols:search" class="item-icon" />
          <span class="flex-1 text-left break-words">{{ item.query }}</span>
          <span class="result-count">{{ item.count }}+</span>
        </button>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref } from "vue";
import eventBus from "@/eventBus";

const router = useRouter();

const searchSuggestions = ref([
  { query: "Tacit Choice in Argentina", count: 15 },
  { query: "Party Autonomy in Switzerland", count: 42 },
  { query: "Public Policy in India", count: 28 },
]);

function handleSuggestionClick(suggestion) {
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
