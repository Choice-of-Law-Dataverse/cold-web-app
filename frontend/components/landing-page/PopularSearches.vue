<template>
  <UCard class="cold-ucard h-full w-full">
    <div class="flex flex-col gap-8">
      <div>
        <h2 class="popular-title text-left md:whitespace-nowrap">
          Popular Searches
        </h2>
      </div>

      <UButton
        v-for="(suggestion, index) in searchSuggestions"
        :key="index"
        class="suggestion-button"
        variant="link"
        @click="handleSuggestionClick(suggestion)"
      >
        <span class="break-words text-left">{{ suggestion }}</span>
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
]);

function handleSuggestionClick(suggestion) {
  eventBus.emit("update-search", suggestion);

  router.push({
    name: "search",
    query: { q: suggestion },
  });
}
</script>
