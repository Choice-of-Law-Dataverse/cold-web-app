<template>
  <footer class="bg-cold-night text-white px-6 md:px-6 py-12 h-[300px]">
    <div
      class="mx-auto grid grid-cols-1 md:grid-cols-12 md:gap-6 items-start"
      style="max-width: var(--container-width); width: 100%"
    >
      <div class="md:col-span-8 flex flex-col gap-3">
        <h1 class="leading-tight">Choice of Law<br />Dataverse</h1>
        <h2 class="leading-snug">
          Funded by the<br />Swiss National Science Foundation
        </h2>
      </div>
      <!-- Footer Links -->
      <h2
        class="md:col-span-4 flex flex-row flex-wrap justify-start md:justify-end gap-8 mt-6 md:mt-0"
      >
        <NuxtLink to="/disclaimer" class="!text-white whitespace-nowrap">
          Disclaimer
        </NuxtLink>
        <NuxtLink to="/about" class="!text-white whitespace-nowrap">
          About
        </NuxtLink>
        <NuxtLink to="/contact" class="!text-white whitespace-nowrap">
          Contact
        </NuxtLink>
      </h2>
    </div>
  </footer>
</template>
