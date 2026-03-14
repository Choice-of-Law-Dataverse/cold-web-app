<template>
  <div
    class="border-cold-gray sticky z-40 w-full border-b backdrop-blur-sm"
    style="
      background: linear-gradient(
        135deg,
        color-mix(in srgb, #6f4dfa 15%, white),
        color-mix(in srgb, #4dfab2 10%, white)
      );
    "
    :class="isScrolled ? 'banner-scrolled' : ''"
  >
    <div
      class="max-w-container mx-auto flex items-center justify-center gap-3 px-3 py-2 sm:gap-4 sm:px-6"
    >
      <p class="text-cold-night text-xs font-medium sm:text-sm">
        <span class="text-cold-purple font-semibold">28 April 2026</span>
        <span class="mx-1.5 hidden sm:inline">&middot;</span>
        <br class="sm:hidden" />
        CoLD Launch Event &mdash; Choice of Law Dataverse in Action
      </p>
      <NuxtLink
        to="/event/launch"
        class="bg-cold-purple hover:bg-cold-purple/90 shrink-0 rounded-sm px-3 py-1 text-xs font-medium text-white transition-colors sm:px-4 sm:py-1.5 sm:text-sm"
      >
        Learn more
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";

const isScrolled = ref(false);

function handleScroll(): void {
  isScrolled.value = window.scrollY > 20;
}

onMounted(() => {
  window.addEventListener("scroll", handleScroll, { passive: true });
  handleScroll();
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});
</script>

<style scoped>
div:first-child {
  top: var(--nav-height);
  transition: top 0.2s ease;
}

div:first-child.banner-scrolled {
  top: var(--nav-height-scrolled);
}
</style>
