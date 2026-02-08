<template>
  <nav
    class="border-cold-gray sticky top-0 z-50 w-full border-b bg-white px-3 sm:px-6"
    :class="{ 'bg-purple-active': isExpanded, 'nav-scrolled': isScrolled }"
  >
    <div class="nav-inner max-w-container mx-auto w-full py-3 sm:py-6 sm:pt-8">
      <div
        class="relative flex items-center justify-between space-x-4 sm:space-x-8"
      >
        <NavSearchBar
          :search-text="searchText"
          :is-mobile="isMobile"
          :is-scrolled="isScrolled"
          :hidden="isMobile && navMenu?.showMenu"
          @update:search-text="searchText = $event"
          @update:is-expanded="isExpanded = $event"
        />

        <NuxtLink
          v-if="!isMobile && !isExpanded && !(isMobile && navMenu?.showMenu)"
          to="/"
          class="desktop-logo"
        >
          <img
            src="https://choiceoflaw.blob.core.windows.net/assets/cold_logo.svg"
            alt="CoLD Logo"
            class="logo-img h-12 w-auto"
          />
        </NuxtLink>
        <NuxtLink
          v-if="isMobile && !isExpanded && !navMenu?.showMenu"
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

        <NavMenu v-if="!isExpanded" ref="navMenu" :is-mobile="isMobile" />
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useRoute } from "vue-router";
import eventBus from "@/eventBus";
import NavSearchBar from "@/components/layout/NavSearchBar.vue";
import NavMenu from "@/components/layout/NavMenu.vue";

const route = useRoute();

const searchText = ref("");
const isExpanded = ref(false);
const isMobile = ref(false);
const isScrolled = ref(false);
const navMenu = ref(null);

function handleScroll() {
  isScrolled.value = window.scrollY > 20;
}

function checkScreenSize() {
  const width = window.innerWidth;
  isMobile.value = width < 640;
}

const updateSearchFromEvent = (query) => {
  searchText.value = query;
};

watch(
  () => route.query.q,
  (newQ) => {
    searchText.value = newQ || "";
  },
);

onMounted(() => {
  checkScreenSize();
  window.addEventListener("resize", checkScreenSize);
  window.addEventListener("scroll", handleScroll, { passive: true });
  handleScroll();

  if (route.query.q) {
    searchText.value = route.query.q;
  }

  eventBus.on("update-search", updateSearchFromEvent);
});

onUnmounted(() => {
  window.removeEventListener("resize", checkScreenSize);
  window.removeEventListener("scroll", handleScroll);
  eventBus.off("update-search", updateSearchFromEvent);
});
</script>

<style scoped>
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

.bg-purple-active {
  background-color: color-mix(
    in srgb,
    var(--color-cold-purple) 5%,
    white
  ) !important;
}

nav {
  min-height: var(--nav-height);
  max-height: var(--nav-height);
  transition:
    min-height 0.2s ease,
    max-height 0.2s ease;
}

.nav-inner {
  transition: padding 0.2s ease;
}

nav.nav-scrolled {
  min-height: var(--nav-height-scrolled);
  max-height: var(--nav-height-scrolled);
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
}
</style>
