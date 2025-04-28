<template>
  <main class="px-6">
    <div class="mx-auto w-full" style="max-width: var(--container-width)">
      <UCard class="cold-ucard">
        <AboutNav />
        <!-- Main Content -->
        <div
          class="main-content prose -space-y-10 flex flex-col gap-12 px-6 w-full"
        >
          <ContentDoc path="/press" />
        </div>
      </UCard>
    </div>
  </main>
</template>

<script setup>
import AboutNav from '~/components/layout/AboutNav.vue'
</script>

<style scoped>
::v-deep(ul) {
  list-style-type: disc !important;
  padding-left: 12px !important;
}
</style>
