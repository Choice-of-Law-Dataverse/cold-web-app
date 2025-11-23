<template>
  <UCard class="cold-ucard h-full w-full">
    <div class="flex flex-col gap-4">
      <div>
        <h2 class="popular-title text-left md:whitespace-nowrap">
          Popular Searches
        </h2>
        <p class="result-value-small">Start with frequent queries</p>
      </div>

      <UButton
        v-for="(suggestion, index) in searchSuggestions"
        :key="index"
        class="suggestion-button"
        variant="link"
        @click="handleSuggestionClick(suggestion)"
      >
        <span class="text-left break-words">{{ suggestion }}</span>
      </UButton>
    </div>
  </UCard>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref } from "vue";
import eventBus from "@/eventBus";

const router = useRouter();

const searchSuggestions = ref([
  "Tacit Choice in Argentina",
  "Party Autonomy in Switzerland",
  "Public Policy in India",
]);

function handleSuggestionClick(suggestion) {
  eventBus.emit("update-search", suggestion);

  router.push({
    name: "search",
    query: { q: suggestion },
  });
}
</script>
