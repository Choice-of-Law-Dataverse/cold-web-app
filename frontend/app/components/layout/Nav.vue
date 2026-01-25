<template>
  <nav
    class="border-cold-gray sticky top-0 z-50 w-full border-b bg-white px-3 sm:px-6"
    :class="{ 'bg-purple-active': isExpanded, 'nav-scrolled': isScrolled }"
  >
    <div class="nav-inner max-w-container mx-auto w-full py-3 sm:py-6 sm:pt-8">
      <div
        class="relative flex items-center justify-between space-x-4 sm:space-x-8"
      >
        <!-- Search Input -->
        <div
          v-show="!(isMobile && showMenu)"
          class="search-container"
          :class="{ expanded: isExpanded }"
        >
          <div class="search-input-row">
            <!-- Collapsed mobile search icon -->
            <button
              v-if="isMobile && !isExpanded"
              class="collapsed-search-icon"
              type="button"
              aria-label="Open search"
              :aria-expanded="isExpanded.toString()"
              @click="handleSearchIconClick"
            >
              <span
                class="iconify i-material-symbols:search"
                aria-hidden="true"
              />
            </button>
            <UInput
              v-show="!isMobile || isExpanded"
              ref="searchInput"
              v-model="searchText"
              size="xl"
              class="input-custom-purple placeholder-purple font-semibold"
              :placeholder="searchPlaceholder"
              autocomplete="off"
              :ui="{
                icon: { trailing: { pointer: '' } },
                wrapper: { base: 'h-12' },
                input: { base: 'h-12' },
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
              @keyup.enter="emitSearch"
              @keydown.esc="clearSearch"
              @focus="expandSearch"
              @blur="collapseSearch"
            >
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
            <button v-if="!isMobile" class="icon-button" @click="emitSearch">
              <span
                class="iconify i-material-symbols:search"
                aria-hidden="true"
              />
            </button>
          </div>

          <!-- Suggestions -->
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

        <!-- Desktop centered logo -->
        <NuxtLink
          v-if="!isMobile && !isExpanded && !(isMobile && showMenu)"
          to="/"
          class="desktop-logo"
        >
          <img
            src="https://choiceoflaw.blob.core.windows.net/assets/cold_logo.svg"
            alt="CoLD Logo"
            class="logo-img h-12 w-auto"
          />
        </NuxtLink>
        <!-- Inline mobile logo for horizontal arrangement -->
        <NuxtLink
          v-if="isMobile && !isExpanded && !showMenu"
          to="/"
          class="mobile-inline-logo flex items-center justify-center"
          aria-label="Home"
        >
          <img
            src="https://choiceoflaw.blob.core.windows.net/assets/cold_logo.svg"
            alt="CoLD Logo"
            class="h-8 w-auto"
          />
        </NuxtLink>

        <!-- Menu/Links Row -->
        <div
          v-if="!isExpanded"
          class="mobile-nav-group flex items-center space-x-4"
        >
          <!-- Mobile: Show menu button and collapsible menu -->
          <template v-if="isMobile">
            <template v-if="!showMenu">
              <button class="menu-button custom-nav-links" @click="openMenu">
                Menu
              </button>
            </template>
            <template v-else>
              <div
                class="flex items-center space-x-3 sm:space-x-6"
                :class="{ 'mobile-menu-links': isMobile }"
              >
                <ULink
                  v-for="(link, i) in links"
                  :key="i"
                  :to="link.to"
                  :class="[
                    'custom-nav-links',
                    { active: route.path.startsWith(link.to) },
                  ]"
                  @click="closeMenu"
                >
                  <span>{{ link.label }}</span>
                </ULink>
                <button
                  class="close-menu-button ml-2"
                  aria-label="Close menu"
                  style="
                    background: none;
                    border: none;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 2.5rem;
                    width: 2.5rem;
                    min-width: 2.5rem;
                    min-height: 2.5rem;
                    z-index: 10;
                  "
                  @click="closeMenu"
                >
                  <span>
                    <UIcon
                      name="i-material-symbols:close"
                      class="mt-[0.3em] ml-[1em] text-[1.3em]"
                    />
                  </span>
                </button>
              </div>
            </template>
          </template>
          <!-- Desktop: Always show menu links -->
          <template v-else>
            <div class="flex items-center space-x-6">
              <ULink
                v-for="(link, i) in links"
                :key="i"
                :to="link.to"
                :class="[
                  'custom-nav-links',
                  { active: route.path.startsWith(link.to) },
                ]"
              >
                <span>{{ link.label }}</span>
              </ULink>
            </div>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import eventBus from "@/eventBus";
import { useJurisdictionLookup } from "@/composables/useJurisdictions";
import { aboutNavLinks, learnNavLinks } from "@/config/navigation";

const router = useRouter();
const route = useRoute();

const basePath = (arr) => `/${arr[0].path.split("/")[1]}`;

const links = [
  { label: "About", to: basePath(aboutNavLinks) },
  { label: "Learn", to: basePath(learnNavLinks) },
  { label: "Contact", to: "/contact" },
];

const showMenu = ref(false);

function openMenu() {
  showMenu.value = true;
  if (isMobile.value) {
    isExpanded.value = false;
    isSearchFocused.value = false;
    showSuggestions.value = false;
  }
  document.addEventListener("mousedown", handleClickAway);
}

function closeMenu() {
  showMenu.value = false;
  document.removeEventListener("mousedown", handleClickAway);
}

function handleClickAway(e) {
  if (!showMenu.value) return;
  const nav = document.querySelector("nav");
  if (nav && !nav.contains(e.target)) {
    closeMenu();
  }
}

function handleClickOutsideMenu(event) {
  if (!showMenu.value) return;
  const nav = document.querySelector("nav");
  if (nav && !nav.contains(event.target)) {
    closeMenu();
  }
}

onMounted(() => {
  document.addEventListener("mousedown", handleClickOutsideMenu);
});

onUnmounted(() => {
  document.removeEventListener("mousedown", handleClickOutsideMenu);
});

const searchText = ref("");
const isExpanded = ref(false);
const isSmallScreen = ref(false);
const isMobile = ref(false);
const suggestions = ref([]);
const showSuggestions = ref(false);
const isSearchFocused = ref(false);
const enableJurisdictionFetch = ref(false);
const isScrolled = ref(false);

function handleScroll() {
  isScrolled.value = window.scrollY > 20;
}

const searchInput = ref(null);

// Minimum search length for jurisdiction suggestions
const MIN_SEARCH_LENGTH = 3;

// Lazily load jurisdiction data - only fetch when user starts typing
const jurisdictionLookup = useJurisdictionLookup(enableJurisdictionFetch);
const { error: jurisdictionError } = jurisdictionLookup;

function updateSuggestions() {
  // Start loading jurisdiction data on first input
  if (!enableJurisdictionFetch.value) {
    enableJurisdictionFetch.value = true;
  }

  if (!searchText.value || searchText.value.trim().length < MIN_SEARCH_LENGTH) {
    suggestions.value = [];
    showSuggestions.value = false;
    return;
  }

  // Don't show suggestions if there's an API error or no data
  if (jurisdictionError.value || !jurisdictionLookup.data.value) {
    suggestions.value = [];
    showSuggestions.value = false;
    return;
  }

  const words = searchText.value
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

  const remainingWords = searchText.value
    .split(/\s+/)
    .map((word) => word.trim())
    .filter(
      (word) =>
        !keywords.some((keyword) => keyword.includes(word.toLowerCase())),
    );

  const newSearchText = remainingWords.join(" ");
  searchText.value = newSearchText;

  isExpanded.value = false;
  isSearchFocused.value = false;
  showSuggestions.value = false;

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

watch(searchText, () => {
  try {
    updateSuggestions();
  } catch (e) {
    console.error("Error updating suggestions:", e);
    suggestions.value = [];
    showSuggestions.value = false;
  }
});

function emitSearch() {
  const query = { ...route.query };

  if (searchText.value.trim()) {
    query.q = searchText.value.trim();
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
  // Start loading jurisdiction data when user focuses search
  enableJurisdictionFetch.value = true;
}

function handleSearchIconClick() {
  if (isMobile.value && !isExpanded.value) {
    expandSearch();
    nextTick(() => {
      const inputEl = searchInput.value?.$el.querySelector("input");
      if (inputEl) inputEl.focus();
    });
  }
}

function collapseSearch() {
  isExpanded.value = false;

  // Delay closing suggestions to allow click handlers to complete
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
  searchText.value = "";
  collapseSearch();
  await nextTick();
  const inputEl = searchInput.value?.$el.querySelector("input");
  if (inputEl) {
    inputEl.blur();
  }
};

const searchPlaceholder = computed(() =>
  isSmallScreen.value ? "Search" : "Search",
);

function checkScreenSize() {
  const width = window.innerWidth;
  isSmallScreen.value = width < 640;
  isMobile.value = width < 640;
}

const updateSearchFromEvent = (query) => {
  searchText.value = query;
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

onMounted(() => {
  checkScreenSize();

  window.addEventListener("resize", checkScreenSize);
  window.addEventListener("scroll", handleScroll, { passive: true });
  handleScroll(); // Check initial scroll position

  if (route.query.q) {
    searchText.value = route.query.q;
  }

  eventBus.on("update-search", updateSearchFromEvent);
});

onUnmounted(() => {
  window.removeEventListener("resize", checkScreenSize);
  window.removeEventListener("scroll", handleScroll);
  eventBus.off("update-search", updateSearchFromEvent);
  document.removeEventListener("mousedown", handleClickAway);
});
</script>

<style scoped>
.input-custom-purple ::v-deep(.placeholder) {
  color: var(--color-cold-purple) !important;
}

.input-custom-purple ::v-deep(.u-input__icon) {
  color: white !important;
  opacity: 0 !important;
}

.input-custom-purple ::v-deep(.u-button .iconify) {
  opacity: 1 !important;
  color: var(--color-cold-purple) !important;
}

.input-custom-purple ::placeholder {
  color: var(--color-cold-purple) !important;
  opacity: 1;
}

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

.input-custom-purple {
  width: 100%;
}

.input-custom-purple :deep(input) {
  padding-left: 2.5rem !important;
}

.icon-button {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-39%);
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-cold-purple);
  padding: 0;
  padding-left: 4px;
}

.icon-button .iconify {
  font-size: 1.5rem;
}

.desktop-logo {
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translate(-50%, -50%);
}

.logo-img {
  display: block;
  transition:
    filter 0.2s ease,
    transform 0.2s ease,
    height 0.2s ease;
}

.desktop-logo:hover .logo-img {
  filter: hue-rotate(-20deg) saturate(1.5) brightness(1.1);
  transform: scale(1.02);
}

a {
  color: var(--color-cold-night) !important;
  text-decoration: none !important;
}

:deep(.custom-nav-links) {
  color: var(--color-cold-night) !important;
  text-decoration: none !important;
  font-weight: 600 !important;
}

:deep(.custom-nav-links.active) {
  text-decoration: underline !important;
  text-underline-offset: 6px !important;
  text-decoration-thickness: 2px !important;
  text-decoration-color: var(--color-cold-purple) !important;
}

:deep(.custom-nav-links:hover) {
  text-decoration: underline !important;
  text-underline-offset: 6px !important;
  text-decoration-thickness: 2px !important;
  text-decoration-color: var(--color-cold-purple) !important;
}

.bg-purple-active {
  background-color: var(--color-cold-purple-alpha) !important;
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

nav {
  min-height: 5rem;
  max-height: 5rem;
  transition:
    min-height 0.2s ease,
    max-height 0.2s ease;
}

.nav-inner {
  transition: padding 0.2s ease;
}

nav.nav-scrolled {
  min-height: 3.5rem;
  max-height: 3.5rem;
}

nav.nav-scrolled .nav-inner {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

nav.nav-scrolled .logo-img {
  height: 1.75rem;
}

nav.nav-scrolled .mobile-inline-logo img {
  height: 1.5rem;
}

@media (min-width: 640px) {
  nav {
    min-height: 7rem;
    max-height: 7rem;
  }

  nav.nav-scrolled {
    min-height: 4rem;
    max-height: 4rem;
  }

  nav.nav-scrolled .nav-inner {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
  }

  nav.nav-scrolled .logo-img {
    height: 2rem;
  }
}

@media (max-width: 639px) {
  .mobile-inline-logo {
    flex: 0 0 auto;
    margin-left: 0.3rem !important;
    margin-right: 0.5rem !important;
  }
  .mobile-nav-group {
    gap: 0.75rem;
  }
  .search-container {
    flex: 0 0 auto;
  }

  .mobile-nav-group > * + * {
    margin-left: 0rem !important;
  }

  .mobile-menu-links {
    margin-left: 3rem;
    margin-top: 0.4rem;
    width: 100%;
    display: flex;
  }

  .mobile-menu-links a:not(:last-of-type) {
    margin-right: 1.1rem;
  }

  .mobile-menu-links .close-menu-button {
    margin-left: auto !important;
  }
  .menu-button.custom-nav-links {
    padding-left: 0.25rem;
    padding-right: 0.25rem;
  }
}

.collapsed-search-icon {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0 0.25rem 0 0;
  color: var(--color-cold-purple);
  height: 2.5rem;
  width: 2.5rem;
  align-items: center;
  justify-content: center;
}

@media (max-width: 639px) {
  .collapsed-search-icon {
    display: inline-flex;
    height: 3rem;
    width: 3rem;
  }
  .collapsed-search-icon .iconify {
    font-size: 1.5rem;
  }
  .search-container:not(.expanded) :deep(.u-input) {
    display: none !important;
  }
  .search-container:not(.expanded) .icon-button {
    display: none;
  }
  .search-container {
    width: auto;
  }
}
</style>
