<template>
  <div style="display: flex; align-items: center">
    <p>Search results</p>
    <div v-if="results && !noResults">
      <SearchResults :data="results" />
    </div>
  </div>
</template>
