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

<script setup>
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { aboutNavLinks } from "@/config/navigation";

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
