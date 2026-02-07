<template>
  <div class="empty-state-container rounded-2xl px-6 py-8">
    <div class="flex flex-col gap-5">
      <div>
        <h2 class="empty-state-title text-xl font-bold">
          Try searching for something
        </h2>
        <p class="empty-state-subtitle mt-1 text-sm">
          Here are some popular searches to get you started
        </p>
      </div>

      <div class="flex w-full flex-col gap-2">
        <button
          v-for="(suggestion, index) in searchSuggestions"
          :key="index"
          class="landing-item-button w-full"
          @click="handleSuggestionClick(suggestion)"
        >
          <Icon name="i-material-symbols:search" class="item-icon" />
          <span class="flex-1 text-left">{{ suggestion }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref } from "vue";
import eventBus from "@/eventBus";

const router = useRouter();

const searchSuggestions = ref([
  "Tacit Choice in Argentina",
  "Party Autonomy in Switzerland",
  "Choice of Law in Contract",
  "Forum Selection Clauses",
  "International Arbitration",
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
.empty-state-container {
  background: var(--gradient-subtle-emphasis);
}

.empty-state-title {
  background: linear-gradient(
    135deg,
    var(--color-cold-night),
    var(--color-cold-purple)
  );
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.empty-state-subtitle {
  color: var(--color-cold-slate);
}
</style>
