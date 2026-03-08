<template>
  <div
    v-show="!hidden"
    class="search-container"
    :class="{ expanded: isExpanded }"
  >
    <div class="search-input-row">
      <button
        v-if="isMobile && !isExpanded"
        class="collapsed-search-icon"
        type="button"
        aria-label="Open search"
        :aria-expanded="isExpanded"
        @click="handleSearchIconClick"
      >
        <span class="iconify i-material-symbols:search" aria-hidden="true" />
      </button>
      <UInput
        v-show="!isMobile || isExpanded"
        ref="searchInput"
        :model-value="searchText"
        size="xl"
        role="combobox"
        :aria-expanded="(isSearchFocused && showSuggestions).toString()"
        aria-controls="search-suggestions"
        aria-autocomplete="list"
        :aria-activedescendant="
          activeSuggestionIndex >= 0
            ? `suggestion-${activeSuggestionIndex}`
            : undefined
        "
        class="placeholder-purple search-input w-full font-semibold"
        :class="{ 'search-input-scrolled': isScrolled }"
        placeholder="Search"
        autocomplete="off"
        :ui="{
          base: 'placeholder:text-[var(--color-cold-purple)] placeholder:opacity-100',
        }"
        :style="{
          width: '100%',
          borderRadius: '0',
          boxShadow: 'none',
          border: 'none',
          backgroundColor: isExpanded
            ? 'transparent'
            : 'var(--color-cold-purple-alpha)',
        }"
        @update:model-value="$emit('update:searchText', $event)"
        @keyup.enter="handleEnterKey"
        @keydown.esc="clearSearch"
        @keydown.down.prevent="handleArrowDown"
        @keydown.up.prevent="handleArrowUp"
        @focus="expandSearch"
        @blur="collapseSearch"
      >
        <template #leading>
          <button
            type="button"
            aria-label="Submit search"
            class="flex cursor-pointer items-center justify-center"
            @click="emitSearch"
          >
            <UIcon
              name="i-material-symbols:search"
              class="text-cold-purple size-6"
            />
          </button>
        </template>
        <template #trailing>
          <button
            v-show="isExpanded"
            type="button"
            aria-label="Clear search"
            class="text-cold-night hover:text-cold-purple flex items-center justify-center"
            @mousedown.prevent
            @click="clearSearch"
          >
            <UIcon name="i-material-symbols:close" class="size-5" />
          </button>
        </template>
      </UInput>
    </div>

    <div
      v-if="isSearchFocused && showSuggestions"
      id="search-suggestions"
      role="listbox"
      class="suggestions border-cold-gray w-full border-b"
    >
      <div class="suggestions-inner">
        <div
          v-for="(suggestion, index) in suggestions"
          :id="`suggestion-${index}`"
          :key="suggestion"
          role="option"
          :aria-selected="index === activeSuggestionIndex"
          class="suggestion-item"
          :class="{ 'suggestion-item-active': index === activeSuggestionIndex }"
          @mousedown.prevent="handleSuggestionClick(suggestion)"
        >
          <span class="suggestion-text"
            >Only show results from {{ suggestion }}</span
          >
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useJurisdictionLookup } from "@/composables/useJurisdictions";

interface Props {
  searchText?: string;
  isMobile?: boolean;
  isScrolled?: boolean;
  hidden?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  searchText: "",
  isMobile: false,
  isScrolled: false,
  hidden: false,
});

const emit = defineEmits<{
  "update:searchText": [value: string];
  "update:isExpanded": [value: boolean];
  search: [];
}>();

const router = useRouter();
const route = useRoute();

const isExpanded = ref(false);
const isSearchFocused = ref(false);
const suggestions = ref<string[]>([]);
const showSuggestions = ref(false);
const enableJurisdictionFetch = ref(false);
const searchInput = ref<{ $el: HTMLElement } | null>(null);
const activeSuggestionIndex = ref(-1);

const MIN_SEARCH_LENGTH = 3;

const jurisdictionLookup = useJurisdictionLookup(enableJurisdictionFetch);
const { error: jurisdictionError } = jurisdictionLookup;

function updateSuggestions() {
  if (!enableJurisdictionFetch.value) {
    enableJurisdictionFetch.value = true;
  }

  if (!props.searchText || props.searchText.trim().length < MIN_SEARCH_LENGTH) {
    suggestions.value = [];
    showSuggestions.value = false;
    return;
  }

  if (jurisdictionError.value || !jurisdictionLookup.data.value) {
    suggestions.value = [];
    showSuggestions.value = false;
    return;
  }

  const words = props.searchText
    .toLowerCase()
    .split(/\s+/)
    .filter((word) => word.length >= MIN_SEARCH_LENGTH);

  const filtered = jurisdictionLookup.findMatchingJurisdictions?.(words) ?? [];

  suggestions.value = filtered.slice(0, 5);
  showSuggestions.value = suggestions.value.length > 0;
  activeSuggestionIndex.value = -1;
}

function handleSuggestionClick(selected: string): void {
  const record = jurisdictionLookup.findJurisdictionByName?.(selected);
  const keywords = record
    ? [
        record.name?.toLowerCase().trim(),
        ...(record.coldId ? [record.coldId.toLowerCase().trim()] : []),
      ].filter(Boolean)
    : [selected?.toLowerCase().trim()].filter(Boolean);

  const remainingWords = props.searchText
    .split(/\s+/)
    .map((word) => word.trim())
    .filter(
      (word) =>
        !keywords.some((keyword) => keyword.includes(word.toLowerCase())),
    );

  const newSearchText = remainingWords.join(" ");
  emit("update:searchText", newSearchText);

  isExpanded.value = false;
  isSearchFocused.value = false;
  showSuggestions.value = false;
  emit("update:isExpanded", false);

  const query = { ...route.query };
  if (newSearchText.trim()) {
    query.q = newSearchText.trim();
  } else {
    delete query.q;
  }
  query.jurisdiction = selected;
  router.push({
    name: "search",
    query,
  });

  nextTick().then(() => {
    const inputEl = searchInput.value?.$el.querySelector("input");
    if (inputEl) {
      inputEl.blur();
    }
  });
}

watch(
  () => props.searchText,
  () => {
    try {
      updateSuggestions();
    } catch (e) {
      console.error("Error updating suggestions:", e);
      suggestions.value = [];
      showSuggestions.value = false;
    }
  },
);

function handleArrowDown() {
  if (!showSuggestions.value || suggestions.value.length === 0) return;
  activeSuggestionIndex.value =
    activeSuggestionIndex.value < suggestions.value.length - 1
      ? activeSuggestionIndex.value + 1
      : 0;
}

function handleArrowUp() {
  if (!showSuggestions.value || suggestions.value.length === 0) return;
  activeSuggestionIndex.value =
    activeSuggestionIndex.value > 0
      ? activeSuggestionIndex.value - 1
      : suggestions.value.length - 1;
}

function handleEnterKey(): void {
  const selected = suggestions.value[activeSuggestionIndex.value];
  if (activeSuggestionIndex.value >= 0 && showSuggestions.value && selected) {
    handleSuggestionClick(selected);
    return;
  }
  emitSearch();
}

function emitSearch() {
  const query = { ...route.query };

  if (props.searchText.trim()) {
    query.q = props.searchText.trim();
  } else {
    delete query.q;
  }

  router.push({
    name: "search",
    query,
  });
  collapseSearch();
  nextTick().then(() => {
    const inputEl = searchInput.value?.$el.querySelector("input");
    if (inputEl) {
      inputEl.blur();
    }
  });
}

function expandSearch() {
  isExpanded.value = true;
  isSearchFocused.value = true;
  enableJurisdictionFetch.value = true;
  emit("update:isExpanded", true);
}

function handleSearchIconClick() {
  if (props.isMobile && !isExpanded.value) {
    expandSearch();
    nextTick(() => {
      const inputEl = searchInput.value?.$el.querySelector("input");
      if (inputEl) inputEl.focus();
    });
  }
}

function collapseSearch() {
  isExpanded.value = false;
  emit("update:isExpanded", false);

  setTimeout(() => {
    if (isSearchFocused.value) {
      isSearchFocused.value = false;
      showSuggestions.value = false;
    } else if (!isSearchFocused.value && showSuggestions.value) {
      showSuggestions.value = false;
    }
  }, 200);
}

const clearSearch = async () => {
  emit("update:searchText", "");
  collapseSearch();
  await nextTick();
  const inputEl = searchInput.value?.$el.querySelector("input");
  if (inputEl) {
    inputEl.blur();
  }
};

function handleGlobalKeydown(e: KeyboardEvent): void {
  if (
    e.key === "s" &&
    !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName ?? "")
  ) {
    e.preventDefault();
    expandSearch();
    nextTick(() => {
      const inputEl = searchInput.value?.$el.querySelector("input");
      if (inputEl) {
        inputEl.focus();
      }
    });
  }
}

onMounted(() => {
  window.addEventListener("keydown", handleGlobalKeydown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleGlobalKeydown);
});
</script>

<style scoped>
.search-container {
  position: relative;
  width: calc(var(--column-width) * 3 + var(--gutter-width) * 2);
  transition: none;
}

.search-container.expanded {
  width: 100%;
  padding-bottom: 0.625rem;
}

.search-input-row {
  position: relative;
  display: flex;
  align-items: center;
}

:deep(.search-input input) {
  height: 3rem;
  transition: height 0.2s ease;
}

:deep(.search-input-scrolled input) {
  height: 2.5rem;
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 100vw;
  max-width: 100vw;
  box-sizing: border-box;
  z-index: 1000;
  background-color: var(--color-cold-purple-fake-alpha);
}

.suggestions-inner {
  width: 100%;
  padding: 0 1.5rem;
  box-sizing: border-box;
}

.suggestion-item {
  padding: 12px 16px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s;
}

.suggestion-item:hover,
.suggestion-item-active {
  background-color: rgba(0, 0, 0, 0.05);
}

.suggestion-text {
  font-weight: 500;
  color: var(--color-cold-night);
}

.collapsed-search-icon {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  color: var(--color-cold-purple);
  height: 2.75rem;
  width: 2.75rem;
  align-items: center;
  justify-content: center;
}

@media (max-width: 639px) {
  .collapsed-search-icon {
    display: inline-flex;
    height: 2.75rem;
    width: 2.75rem;
  }
  .collapsed-search-icon .iconify {
    font-size: 1.5rem;
    line-height: 1;
  }
  .search-container:not(.expanded) .icon-button {
    display: none;
  }
  .search-container {
    width: auto;
  }
}
</style>
