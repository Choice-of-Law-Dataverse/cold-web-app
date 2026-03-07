<template>
  <div v-if="!hidden" class="mobile-nav-group flex items-center space-x-4">
    <template v-if="isMobile">
      <template v-if="!showMenu">
        <button
          class="menu-button custom-nav-links"
          :aria-expanded="showMenu"
          aria-controls="mobile-nav-menu"
          @click="openMenu"
        >
          Menu
        </button>
      </template>
      <template v-else>
        <div
          id="mobile-nav-menu"
          class="flex items-center space-x-3 sm:space-x-6"
          :class="{ 'mobile-menu-links': isMobile }"
          @keydown.esc="closeMenu"
        >
          <ULink
            v-for="(link, i) in links"
            :key="i"
            :to="link.to"
            :aria-current="route.path.startsWith(link.to) ? 'page' : undefined"
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
              height: 2.75rem;
              width: 2.75rem;
              min-width: 2.75rem;
              min-height: 2.75rem;
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
    <template v-else>
      <div class="flex items-center space-x-6">
        <ULink
          v-for="(link, i) in links"
          :key="i"
          :to="link.to"
          :aria-current="route.path.startsWith(link.to) ? 'page' : undefined"
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
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { aboutNavLinks, learnNavLinks } from "@/config/navigation";

interface Props {
  isMobile?: boolean;
  hidden?: boolean;
}

withDefaults(defineProps<Props>(), {
  isMobile: false,
  hidden: false,
});

const route = useRoute();

function basePath(arr: { path: string }[]): string {
  return `/${arr[0]?.path.split("/")[1] ?? ""}`;
}

const links = [
  { label: "About", to: basePath(aboutNavLinks) },
  { label: "Learn", to: basePath(learnNavLinks) },
  { label: "Contact", to: "/contact" },
];

const showMenu = ref(false);

function openMenu(): void {
  showMenu.value = true;
  document.addEventListener("mousedown", handleClickAway);
}

function closeMenu(): void {
  showMenu.value = false;
  document.removeEventListener("mousedown", handleClickAway);
}

function handleClickAway(e: MouseEvent): void {
  if (!showMenu.value) return;
  const nav = document.querySelector("nav");
  if (nav && !nav.contains(e.target as Node)) {
    closeMenu();
  }
}

function handleClickOutsideMenu(event: MouseEvent): void {
  if (!showMenu.value) return;
  const nav = document.querySelector("nav");
  if (nav && !nav.contains(event.target as Node)) {
    closeMenu();
  }
}

onMounted(() => {
  document.addEventListener("mousedown", handleClickOutsideMenu);
});

onUnmounted(() => {
  document.removeEventListener("mousedown", handleClickOutsideMenu);
  document.removeEventListener("mousedown", handleClickAway);
});

defineExpose({ showMenu });
</script>

<style scoped>
:deep(.custom-nav-links) {
  color: var(--color-cold-night);
  text-decoration: none;
  font-weight: 600;
}

:deep(.custom-nav-links.active) {
  text-decoration: underline;
  text-underline-offset: 6px;
  text-decoration-thickness: 2px;
  text-decoration-color: var(--color-cold-purple);
}

:deep(.custom-nav-links:hover) {
  text-decoration: underline;
  text-underline-offset: 6px;
  text-decoration-thickness: 2px;
  text-decoration-color: var(--color-cold-purple);
}

@media (max-width: 639px) {
  .mobile-nav-group {
    gap: 0.75rem;
  }

  .mobile-nav-group > * + * {
    margin-left: 0rem;
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
    margin-left: auto;
  }
  .menu-button.custom-nav-links {
    padding-left: 0.25rem;
    padding-right: 0.25rem;
  }
}
</style>
