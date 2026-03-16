<template>
  <div class="results-content mt-4">
    <div v-if="loading && !results.length" class="results-grid">
      <LoadingCard v-for="n in 6" :key="`loading-${n}`" />
    </div>

    <EmptySearchState v-else-if="!loading && !results.length && !hasQuery" />

    <NoSearchResults v-else-if="!loading && !results.length" />

    <template v-else>
      <div class="results-grid">
        <div
          v-for="(resultData, key) in results"
          :key="key"
          class="result-item"
        >
          <component
            :is="getResultComponent(resultData.sourceTable as string)"
            :result-data="resultData"
            :card-type="resultData.sourceTable as string"
          />
        </div>
        <LoadingCard
          v-if="loading && results.length"
          class="py-4 text-center"
        />
      </div>

      <div v-if="canLoadMore && !loading" class="mt-16 mb-4 text-center">
        <UButton
          native-type="button"
          variant="link"
          size="lg"
          icon="i-material-symbols:arrow-cool-down"
          :disabled="loading"
          @click.prevent="$emit('load-more')"
        >
          Load More Results
        </UButton>
      </div>

      <div v-if="!loading" class="result-value-small pt-4 text-center">
        <UButton
          to="https://choice-of-law-dataverse.github.io/search-algorithm"
          variant="link"
          target="_blank"
        >
          Learn How the Search Works
        </UButton>
        <UIcon
          name="i-material-symbols:open-in-new"
          class="ml-[-6px] inline-block"
          style="color: var(--color-cold-purple); position: relative; top: 2px"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { Component } from "vue";
import SearchResultCardContent from "@/components/search-results/SearchResultCardContent.vue";
import AnswerSearchCard from "@/components/search-results/AnswerSearchCard.vue";
import NoSearchResults from "@/components/search-results/NoSearchResults.vue";
import EmptySearchState from "@/components/search-results/EmptySearchState.vue";
import LoadingCard from "@/components/layout/LoadingCard.vue";
import type { AnySearchResult } from "@/types/search";

defineProps<{
  results: AnySearchResult[];
  loading: boolean;
  canLoadMore: boolean;
  hasQuery: boolean;
}>();

defineEmits<{
  (e: "load-more"): void;
}>();

const customCards: Record<string, Component> = {
  Answers: AnswerSearchCard,
};

const getResultComponent = (sourceTable: string) =>
  customCards[sourceTable] || SearchResultCardContent;
</script>
