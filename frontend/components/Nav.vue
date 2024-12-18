<template>
  <nav class="main-navigation">
    <div class="container">
      <div class="inner-content flex items-center justify-between">
        <!-- Web App Name aligned to the first column -->
        <div>
          <h1><a href="/">CoLD</a></h1>
        </div>

        <!-- Search Input positioned from the center of column 2 to the end of column 10 -->
        <div class="search-container">
          <UInput
            size="xl"
            v-model="searchText"
            @keyup.enter="emitSearch"
            class="input-custom-purple placeholder-purple"
            placeholder="Search the entire Dataverse"
            icon="i-material-symbols:search"
            :trailing="true"
            style="
              width: 100%; /* Full width inside the container */
              border-radius: 0 !important;
              box-shadow: none !important;
              border-width: 1px !important;
              border-color: var(--color-cold-purple) !important;
            "
          />
          <!-- Clickable icon overlay button -->
          <button @click="emitSearch" class="icon-button">
            <span
              class="iconify i-material-symbols:search"
              aria-hidden="true"
            ></span>
          </button>
        </div>

        <!-- Navigation Links, aligned in columns 11 and 12 -->
        <div>
          <ULink
            v-for="(link, index) in links"
            :key="index"
            :to="link.to"
            :class="['custom-nav-links', { active: route.path === link.to }]"
          >
            <span>{{ link.label }}</span>
          </ULink>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const searchText = ref('')
const router = useRouter()
const route = useRoute()

const links = [
  { label: 'About', to: '/about' },
  { label: 'Contact', to: '/contact' },
]

function emitSearch() {
  if (searchText.value.trim()) {
    router.push({ name: 'search', query: { q: searchText.value } })
  }
}

onMounted(() => {
  if (route.query.q) {
    searchText.value = route.query.q
  }
})
</script>

<style scoped>
.input-custom-purple ::v-deep(.placeholder) {
  color: var(--color-cold-purple) !important;
}

/* Make the original input's icon white and thus invisible */
/* I.e., the icon that's not clickable */
.input-custom-purple ::v-deep(.iconify) {
  color: white !important;
  opacity: 0 !important;
}

.input-custom-purple ::placeholder {
  color: var(--color-cold-purple) !important;
  opacity: 1;
}

.main-navigation {
  width: 100%;
  height: 112px;
  background-color: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
}

.container {
  max-width: 100vw;
  padding: 0 var(--gutter-width);
}

.inner-content {
  max-width: var(--container-width);
  margin: 0 auto;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.search-container {
  position: relative; /* Allow absolute positioning for icon */
  width: calc(
    var(--column-width) * 9 + var(--gutter-width) * 8
  ); /* 9-column width */
  margin-left: calc(var(--column-width) / 2);
}

.input-custom-purple {
  width: 100%; /* Ensures the input spans the container width */
}

.icon-button {
  position: absolute;
  right: 10px; /* Adjust based on the right padding of input */
  top: 50%;
  transform: translateY(-39%); /* Center vertically */
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-cold-purple); /* Match icon color */
  padding: 0;
}

.icon-button .iconify {
  font-size: 1.5rem; /* Adjust icon size */
}

a {
  color: var(--color-cold-night) !important;
  text-decoration: none !important;
}

:deep(.custom-nav-links) {
  color: var(--color-cold-night) !important; /* Apply custom color */
  text-decoration: none !important; /* Remove underline */
  margin-left: 48px;
  font-weight: 600;
}

:deep(.custom-nav-links.active) {
  text-decoration: underline !important;
  text-underline-offset: 6px !important;
  text-decoration-thickness: 2px !important;
  text-decoration-color: var(--color-cold-purple) !important;
}
</style>
