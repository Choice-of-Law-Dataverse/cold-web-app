<template>
  <nav>
    <div class="nav-wrapper scrollbar-hidden relative overflow-x-auto">
      <ul class="relative z-0 inline-flex list-none items-center space-x-4">
        <li
          v-for="link in links"
          :key="link.key"
          :class="[
            'result-value-small cursor-pointer whitespace-nowrap',
            activeTab === link.key ? 'active font-bold' : 'text-cold-night',
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
  position: relative;
  z-index: 0;
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

ul::-webkit-scrollbar {
  display: none;
}

li.active {
  text-decoration: underline;
  text-underline-offset: 6px;
  text-decoration-thickness: 2px;
  text-decoration-color: var(--color-cold-purple);
}

.flex li {
  padding: 0.5rem 1.5rem;
}

/* ::v-deep(ul) {
  list-style-type: disc;
  padding-left: 12px;
} */
</style>
