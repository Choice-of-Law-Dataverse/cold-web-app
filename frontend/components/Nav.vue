<template>
  <nav class="main-navigation">
    <div class="container">
      <div class="inner-content flex items-center justify-between">
        <!-- Web App Name aligned to the first column -->
        <div class="font-bold whitespace-nowrap">
          <a href="/">CoLD</a>
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
              border-radius: 0 !important;
              box-shadow: none !important;
              border-width: 1px !important;
              border-color: var(--color-cold-purple) !important;
            "
          />
        </div>

        <!-- Navigation Links, naturally aligned in columns 11 and 12 -->
        <div class="nav-links-container" style="margin-right: -10px">
          <UHorizontalNavigation :links="links" />
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const searchText = ref('')
const router = useRouter()

const links = [
  { label: 'About', to: '/about' },
  { label: 'Contact', to: '/contact' },
]

function emitSearch() {
  if (searchText.value.trim()) {
    router.push({ name: 'search', query: { q: searchText.value } })
  }
}
</script>

<style scoped>
.input-custom-purple ::v-deep(.u-input-icon),
.input-custom-purple ::v-deep(.placeholder),
.input-custom-purple ::v-deep(.iconify) {
  color: var(--color-cold-purple) !important;
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
  flex: 0 0 calc(var(--column-width) * 9 + var(--gutter-width) * 8);
  margin-left: calc(var(--column-width) / 2);
}

/* .nav-links-container {
  margin-right: 12px;
} */
</style>
