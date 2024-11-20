<script setup lang="ts">
import PopularSearches from '~/components/PopularSearches.vue'
import CountrySelectMenu from '~/components/CountrySelectMenu.vue'
</script>

<template>
  <div class="container">
    <div class="col-span-12">
      <h1>Choice of Law Dataverse</h1>
      <h2>Find relevant case law and choice of law answers for your case.</h2>
      <PopularSearches />
      <CountrySelectMenu />
    </div>
  </div>
</template>

<style scoped>
h1 {
  margin-bottom: 12px;
}

h2 {
  margin-bottom: 42px;
}
</style>
