<template>
  <nav>
    <div class="nav-wrapper scrollbar-hidden relative overflow-x-auto">
      <ul class="relative z-0 inline-flex list-none items-center space-x-4">
        <li
          v-for="link in links"
          :key="link.key"
          :class="[
            'result-value-small cursor-pointer whitespace-nowrap',
            activeTab === link.key
              ? 'active font-bold text-cold-purple'
              : 'text-cold-night',
          ]"
          @click="setActiveTab(link.path)"
        >
          {{ link.label }}
        </li>
      </ul>
    </div>
  </nav>
</template>

<script setup>
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { aboutNavLinks } from "@/config/pageConfigs.js";

const props = defineProps({
  links: {
    type: Array,
    default: () => aboutNavLinks,
  },
});

const links = props.links;
const router = useRouter();
const route = useRoute();

const activeTab = computed(() => {
  const segment = route.path.split("/").pop();
  return segment || links[0].key;
});

const setActiveTab = (path) => {
  router.push(path);
};
</script>

<style scoped>
.nav-wrapper {
  position: relative !important;
  z-index: 0 !important;
  margin-bottom: -1.5em;

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
  border-bottom: 0 solid var(--color-cold-gray);
}

ul::before {
  content: "";
  position: absolute;
  bottom: 39px;
  left: 0;
  width: 100%;
  height: 1px;
  background-color: var(--color-cold-gray);
  z-index: -1;
}

ul::-webkit-scrollbar {
  display: none;
}

li {
  position: relative !important;
  z-index: 1 !important;
}

li.active {
  z-index: 2 !important;
}

li.active::after {
  content: "";
  position: absolute !important;
  left: 0;
  bottom: -9px;
  width: 100%;
  height: 1px;
  background-color: var(--color-cold-purple);
  z-index: 3 !important;
  pointer-events: none;
}

.list-none {
  list-style: none !important;
}

.flex li {
  padding: 0.5rem 1.5rem;
}

::v-deep(ul) {
  list-style-type: disc !important;
  padding-left: 12px !important;
}
</style>
