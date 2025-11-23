<template>
  <div class="flex h-full w-full items-center justify-center py-12">
    <UCard class="cold-ucard w-full max-w-2xl">
      <div class="flex flex-col gap-8">
        <div>
          <h2 class="text-left text-2xl font-semibold md:whitespace-nowrap">
            Try searching for something
          </h2>
          <p class="mt-2 text-gray-600">
            Here are some popular searches to get you started:
          </p>
        </div>

        <div class="flex flex-col gap-2">
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
      </div>
    </UCard>
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
.suggestion-button {
  width: 100%;
  justify-content: flex-start;
  text-align: left;
}

.suggestion-button:hover {
  text-decoration: underline;
}
</style>
