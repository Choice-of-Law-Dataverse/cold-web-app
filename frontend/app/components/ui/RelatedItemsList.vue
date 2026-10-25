<template>
  <div v-if="shouldShowSection">
    <div v-if="isLoading">
      <LoadingBar />
    </div>
    <InlineError v-else-if="error" :error="error" />
    <div v-else-if="items.length" class="result-value-small">
      <div
        v-if="isJurisdictionList"
        class="mb-2 flex flex-row flex-wrap items-center gap-x-6 gap-y-2"
      >
        <EntityLink
          v-for="item in visibleItems"
          :key="item.id"
          :id="item.id"
          :title="item.title"
          :base-path="basePath"
          variant="jurisdiction"
          class="-ml-2"
        >
          <div class="flag-wrapper">
            <JurisdictionFlag
              :iso3="item.id"
              class="item-flag"
              :alt="`${item.title} flag`"
            />
          </div>
          {{ item.title }}
        </EntityLink>
      </div>
      <div v-else class="mb-2 flex flex-row flex-wrap gap-x-6 gap-y-2">
        <EntityLink
          v-for="item in visibleItems"
          :key="item.id"
          :id="item.id"
          :title="item.title"
          :base-path="basePath"
          :badge="item.badge"
        />
      </div>
      <ShowMoreLess
        v-if="items.length > SHOW_MORE_THRESHOLD"
        v-model:is-expanded="isExpanded"
      />
    </div>
    <p
      v-else-if="emptyValueBehavior.action === 'display'"
      class="result-value-small"
    >
      &mdash;
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import InlineError from "@/components/ui/InlineError.vue";
import EntityLink from "@/components/ui/EntityLink.vue";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";
import ShowMoreLess from "@/components/ui/ShowMoreLess.vue";
import type { RelatedItem, EmptyValueBehavior } from "@/types/ui";

const SHOW_MORE_THRESHOLD = 20;

const props = withDefaults(
  defineProps<{
    items?: RelatedItem[];
    isLoading?: boolean;
    error?: Error;
    basePath: string;
    emptyValueBehavior?: EmptyValueBehavior;
  }>(),
  {
    items: () => [],
    isLoading: false,
    error: undefined,
    emptyValueBehavior: () => ({
      action: "hide" as const,
    }),
  },
);

const isExpanded = ref(false);

const hasItems = computed(() => props.items.length > 0);

const isJurisdictionList = computed(() => props.basePath === "/jurisdiction");

const visibleItems = computed(() =>
  isExpanded.value || props.items.length <= SHOW_MORE_THRESHOLD
    ? props.items
    : props.items.slice(0, SHOW_MORE_THRESHOLD),
);

const shouldShowSection = computed(
  () =>
    props.isLoading ||
    hasItems.value ||
    (!hasItems.value && props.emptyValueBehavior.action === "display"),
);
</script>
