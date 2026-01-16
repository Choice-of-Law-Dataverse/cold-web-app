<template>
  <UCard class="cold-ucard gradient-top-border h-full w-full">
    <div class="flex flex-col gap-4">
      <div>
        <h2 class="card-title text-left md:whitespace-nowrap">
          Top Literature Themes
        </h2>
        <p class="card-subtitle">Browse essential legal publications</p>
      </div>

      <div class="flex flex-col gap-2">
        <button
          v-for="(suggestion, index) in searchSuggestions"
          :key="index"
          class="landing-item-button"
          @click="handleSuggestionClick(suggestion)"
        >
          <Icon name="i-material-symbols:book-outline" class="item-icon" />
          <span class="break-words text-left">{{ suggestion }}</span>
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
