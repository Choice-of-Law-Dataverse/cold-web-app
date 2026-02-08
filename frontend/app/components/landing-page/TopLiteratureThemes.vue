<template>
  <UCard class="h-full w-full" :ui="{ body: '!p-0' }">
    <div class="gradient-top-border" />
    <div class="flex flex-col gap-4 p-4 sm:p-6">
      <div>
        <h2 class="card-title text-left md:whitespace-nowrap">
          Top Literature Themes
        </h2>
        <p class="card-subtitle">Browse essential legal publications</p>
      </div>

      <div class="flex w-full flex-col gap-2">
        <button
          v-for="(suggestion, index) in searchSuggestions"
          :key="index"
          class="landing-item-button type-literature w-full"
          @click="handleSuggestionClick(suggestion)"
        >
          <Icon name="i-material-symbols:book-outline" class="item-icon" />
          <span class="text-left break-words">{{ suggestion }}</span>
        </button>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref } from "vue";

const router = useRouter();

const searchSuggestions = ref([
  "Arbitration",
  "Rules of law",
  "Overriding mandatory rules",
]);

function handleSuggestionClick(suggestion) {
  router.push({
    name: "search",
    query: { theme: suggestion, type: "Literature" },
  });
}
</script>
