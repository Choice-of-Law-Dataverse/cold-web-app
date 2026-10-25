<template>
  <div class="bg-cold-bg flex min-h-dvh flex-col">
    <a href="#main-content" class="skip-link">Skip to main content</a>
    <Nav />

    <main
      id="main-content"
      class="main-content isolate flex-1 px-3 py-6 sm:px-6 sm:py-12"
      :class="{ 'sm:mr-[24rem]': isDrawerOpen }"
    >
      <div class="max-w-container mx-auto w-full">
        <div class="flex flex-col gap-4 sm:gap-6">
          <ErrorBoundary>
            <NuxtPage :transition="{ name: 'page', mode: 'out-in' }" />
          </ErrorBoundary>
        </div>
      </div>
    </main>

    <Footer />

    <div aria-live="polite" aria-atomic="true" class="sr-only">
      {{ announcement }}
    </div>

    <EntityDrawer v-if="hasOpenedDrawer" />
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, onMounted, ref, watch } from "vue";
import Nav from "@/components/layout/Nav.vue";
import Footer from "@/components/layout/Footer.vue";
import ErrorBoundary from "@/components/ui/ErrorBoundary.vue";
import { useScreenAnnouncer } from "@/composables/useScreenAnnouncer";
import { useEntityDrawer } from "@/composables/useEntityDrawer";

const EntityDrawer = defineAsyncComponent(
  () => import("@/components/entity/EntityDrawer.vue"),
);

const { announcement } = useScreenAnnouncer();
const { isOpen: isDrawerOpen } = useEntityDrawer();

const hasOpenedDrawer = ref(false);

watch(isDrawerOpen, (open) => {
  if (open) hasOpenedDrawer.value = true;
});

onMounted(() => {
  if (hasOpenedDrawer.value) return;
  const schedule =
    typeof window.requestIdleCallback === "function"
      ? (cb: () => void) => window.requestIdleCallback(cb, { timeout: 2500 })
      : (cb: () => void) => window.setTimeout(cb, 1500);
  schedule(() => {
    hasOpenedDrawer.value = true;
  });
});
</script>

<style scoped>
/*
 * Main content min-height calculation:
 * - Ensures stable layout during page transitions (prevents footer jump)
 * - Allows footer to peek above fold, hinting at more content
 *
 * Formula: 100dvh - nav - main-margin - footer-margin
 */
.main-content {
  min-height: calc(100dvh - var(--nav-height) - var(--banner-height) - 10rem);
}
</style>

<style>
@reference "@/assets/styles.css";

.skip-link {
  @apply absolute top-auto -left-[9999px] z-[9999] h-px w-px overflow-hidden rounded-br-lg px-6 py-3 font-semibold text-white no-underline;
  background: var(--color-cold-purple);
}

.skip-link:focus-visible {
  @apply fixed top-0 left-0 h-auto w-auto outline-2 outline-offset-2;
  outline-color: var(--color-cold-purple);
}
</style>
