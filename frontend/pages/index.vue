<template>
  <div class="container">
    <div class="col-span-12">
      <h1>Choice of Law Dataverse</h1>
      <h2>Find relevant case law and choice of law answers for your case.</h2>
      <PopularSearches />
      <JurisdictionMap />
      <CountrySelectMenu />
      <div style="width: 60%">
        <PlotCourtDecisionsJurisdiction />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import PopularSearches from '~/components/PopularSearches.vue'
import JurisdictionMap from '~/components/JurisdictionMap.vue'
import CountrySelectMenu from '~/components/TempJurisdictionPicker.vue'
import PlotCourtDecisionsJurisdiction from '~/components/PlotCourtDecisionsJurisdiction.vue'
</script>

<style scoped>
h1 {
  margin-bottom: 12px;
}

h2 {
  margin-bottom: 42px;
}
</style>
