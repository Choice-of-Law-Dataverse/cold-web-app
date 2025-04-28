<template>
  <nav>
    <div class="nav-wrapper relative">
      <ul
        class="flex items-center space-x-4 border-b border-gray-200 dark:border-gray-800 list-none overflow-x-auto scrollbar-hidden relative z-0"
      >
        <li
          v-for="link in links"
          :key="link.key"
          :class="[
            'result-value-small cursor-pointer whitespace-nowrap',
            activeTab === link.key
              ? 'active font-bold text-cold-purple'
              : 'text-cold-night',
          ]"
          @click="setActiveTab(link.key)"
        >
          {{ link.label }}
        </li>
      </ul>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const links = [
  { label: 'About CoLD', key: 'about-cold' },
  { label: 'Team', key: 'team' },
  { label: 'Supporters', key: 'supporters' },
  { label: 'Endorsements', key: 'endorsements' },
  { label: 'Press', key: 'press' },
]

const activeTab = computed(() => {
  const segment = route.path.split('/').pop()
  return segment || 'about-cold'
})

const setActiveTab = (key) => {
  router.push(`/about/${key}`)
}
</script>

<style scoped>
.nav-wrapper {
  position: relative !important;
  z-index: 0 !important;
}

ul {
  overflow-x: auto;
  white-space: nowrap;
  position: relative;
  border-bottom: 0px solid var(--color-cold-gray);
  -ms-overflow-style: none;
  scrollbar-width: none;
}

ul::before {
  content: '';
  position: absolute;
  bottom: 15px;
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
  content: '';
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
