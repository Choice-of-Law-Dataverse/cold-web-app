<template>
  <footer class="bg-cold-night text-white px-6 py-12 min-h-[300px] mt-24">
    <div
      class="mx-auto grid grid-cols-1 md:grid-cols-12 md:gap-6 items-start"
      style="max-width: var(--container-width)"
    >
      <div class="md:col-span-8 flex flex-col gap-3 mt-4">
        <img
          src="https://choiceoflaw.blob.core.windows.net/assets/cold_flag_footer.svg"
          style="width: 100px"
          class="mb-6"
        />
        <h2 class="!font-bold leading-tight">Choice of Law<br />Dataverse</h2>
        <p class="leading-snug">
          Funded by the<br />Swiss National Science Foundation
        </p>
      </div>
      <!-- Footer Links -->
      <div
        class="md:col-span-4 flex flex-row md:justify-end gap-8 mt-12 md:mt-4 mb-4 md:mb-0 whitespace-nowrap"
      >
        <NuxtLink to="/disclaimer" class="!text-white whitespace-nowrap">
          Disclaimer
        </NuxtLink>
        <NuxtLink to="/contact" class="!text-white whitespace-nowrap">
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
