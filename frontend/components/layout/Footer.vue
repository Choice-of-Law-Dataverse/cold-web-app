<template>
  <footer class="mt-24 min-h-[300px] bg-cold-night px-6 py-12 text-white">
    <div
      class="mx-auto grid max-w-container grid-cols-1 items-start md:grid-cols-12 md:gap-6"
    >
      <div class="mt-4 flex flex-col gap-3 md:col-span-8">
        <img
          src="https://choiceoflaw.blob.core.windows.net/assets/cold_flag_footer.svg"
          class="w-25 mb-6"
        >
        <h2 class="!font-bold leading-tight">Choice of Law<br >Dataverse</h2>
        <p class="leading-snug">
          Funded by the<br >Swiss National Science Foundation
        </p>
      </div>
      <!-- Footer Links -->
      <div
        class="mb-4 mt-12 flex flex-row gap-8 whitespace-nowrap md:col-span-4 md:mb-0 md:mt-4 md:justify-end"
      >
        <NuxtLink to="/disclaimer" class="whitespace-nowrap !text-white">
          Disclaimer
        </NuxtLink>
        <NuxtLink to="/contact" class="whitespace-nowrap !text-white">
          Contact
        </NuxtLink>
      </div>
    </div>
  </footer>
</template>

<style scoped>
a {
  font-weight: 600 !important;
}

h2 {
  color: white !important;
}
</style>
