<template>
  <nav>
    <div class="nav-wrapper scrollbar-hidden relative overflow-x-auto">
      <ul class="relative z-0 inline-flex list-none items-center gap-1">
        <li
          v-for="link in links"
          :key="link.key"
          class="section-nav-item"
          :class="{ 'section-nav-item-active': activeTab === link.key }"
          @click="setActiveTab(link.path)"
        >
          {{ link.label }}
        </li>
      </ul>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { aboutNavLinks } from "@/config/navigation";

interface NavLink {
  label: string;
  key: string;
  path: string;
}

interface Props {
  links?: NavLink[];
}

const props = withDefaults(defineProps<Props>(), {
  links: () => aboutNavLinks,
});

const router = useRouter();
const route = useRoute();

const activeTab = computed(() => {
  const segment = route.path.split("/").pop();
  return segment || props.links[0]?.key || "";
});

function setActiveTab(path: string): void {
  router.push(path);
}
</script>

<style scoped>
.nav-wrapper {
  position: relative;
  z-index: 0;
  margin-bottom: 1rem;
  overflow-x: auto;
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.nav-wrapper::-webkit-scrollbar {
  display: none;
}

ul {
  display: inline-flex;
  width: max-content;
  min-width: 100%;
  white-space: nowrap;
  position: relative;
  border-bottom: 2px solid rgb(229 231 235);
}

ul::-webkit-scrollbar {
  display: none;
}
</style>

<style>
@reference "tailwindcss";

.nav-tab,
.section-nav-item {
  @apply text-cold-night relative -mb-0.5 cursor-pointer rounded-t-lg px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-all duration-150;
}

.nav-tab:hover,
.section-nav-item:hover {
  background: var(--gradient-subtle);
}

.nav-tab:focus-visible,
.section-nav-item:focus-visible {
  @apply outline-cold-purple outline-2 -outline-offset-2;
}

.nav-tab--bordered {
  @apply border-b-2 border-gray-200;
}

.nav-tab--active,
.section-nav-item-active {
  @apply border-cold-purple text-cold-purple border-b-2 font-semibold;
}
</style>
