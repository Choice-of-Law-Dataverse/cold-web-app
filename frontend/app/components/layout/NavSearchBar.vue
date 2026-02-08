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
        :aria-expanded="isExpanded.toString()"
        @click="handleSearchIconClick"
      >
        <span class="iconify i-material-symbols:search" aria-hidden="true" />
      </button>
      <UInput
        v-show="!isMobile || isExpanded"
        ref="searchInput"
        :model-value="searchText"
        size="xl"
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
        @keyup.enter="emitSearch"
        @keydown.esc="clearSearch"
        @focus="expandSearch"
        @blur="collapseSearch"
      >
        <template #leading>
          <button
            type="button"
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
      class="suggestions border-cold-gray w-full border-b"
    >
      <div class="suggestions-inner">
        <div
          v-for="suggestion in suggestions"
          :key="suggestion"
          class="suggestion-item"
          @click="handleSuggestionClick(suggestion)"
        >
          <span class="suggestion-text"
            >Only show results from {{ suggestion }}</span
          >
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useJurisdictionLookup } from "@/composables/useJurisdictions";

const props = defineProps({
  searchText: {
    type: String,
    default: "",
  },
  isMobile: {
    type: Boolean,
    default: false,
  },
  isScrolled: {
    type: Boolean,
    default: false,
  },
  hidden: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:searchText", "update:isExpanded", "search"]);

const router = useRouter();
const route = useRoute();

const isExpanded = ref(false);
const isSearchFocused = ref(false);
const suggestions = ref([]);
const showSuggestions = ref(false);
const enableJurisdictionFetch = ref(false);
const searchInput = ref(null);

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
}

function handleSuggestionClick(selected) {
  const record = jurisdictionLookup.findJurisdictionByName?.(selected);
  const keywords = record
    ? [
        record.Name?.toLowerCase().trim(),
        ...(record.alpha3Code ? [record.alpha3Code.toLowerCase().trim()] : []),
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

function handleGlobalKeydown(e) {
  if (
    e.key === "s" &&
    !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)
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
  position: relative !important;
  width: calc(var(--column-width) * 3 + var(--gutter-width) * 2);
  transition: none !important;
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

.suggestion-item:hover {
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
  height: 2.5rem;
  width: 2.5rem;
  align-items: center;
  justify-content: center;
}

@media (max-width: 639px) {
  .collapsed-search-icon {
    display: inline-flex;
    height: 2.5rem;
    width: 2.5rem;
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
