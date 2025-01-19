<template>
  <div class="bg-cold-bg min-h-screen">
    <Nav />
    <UContainer class="mt-12" />
    <main class="flex-1 flex flex-col">
      <NuxtPage />
    </main>
    <!-- <Footer /> -->
  </div>
</template>

<style scoped>
/* main {
  min-height: calc(
    100vh - 112px - 80px
  ); /* Adjust based on header and footer heights */
/*} */
</style>
