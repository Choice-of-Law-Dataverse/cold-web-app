<template>
  <UCard class="cold-ucard landing-card h-full w-full">
    <div class="flex flex-col gap-4">
      <div>
        <h2 class="card-title text-left">Popular Searches</h2>
        <p class="card-subtitle">Start with frequent queries</p>
      </div>

      <div class="flex flex-col gap-2">
        <button
          v-for="(suggestion, index) in searchSuggestions"
          :key="index"
          class="landing-item-button"
          @click="handleSuggestionClick(suggestion)"
        >
          <Icon name="i-material-symbols:search" class="item-icon" />
          <span class="break-words text-left">{{ suggestion }}</span>
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
