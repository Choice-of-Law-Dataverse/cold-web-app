<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container flex flex-col md:flex-row gap-8">
      <h2 class="popular-title text-left md:whitespace-nowrap">
        Recent Domestic Instruments
      </h2>
    </div>
    <ul>
      <li>
        <UButton
          class="suggestion-button"
          variant="link"
          icon="i-material-symbols:arrow-forward"
          trailing
        >
          <span class="break-words text-left">Domestic Instrument 1</span>
        </UButton>
      </li>
      <li>
        <UButton
          class="suggestion-button"
          variant="link"
          icon="i-material-symbols:arrow-forward"
          trailing
        >
          <span class="break-words text-left">Domestic Instrument 2</span>
        </UButton>
      </li>
      <li>
        <UButton
          class="suggestion-button"
          variant="link"
          icon="i-material-symbols:arrow-forward"
          trailing
        >
          <span class="break-words text-left">Domestic Instrument 3</span>
        </UButton>
      </li>
    </ul>
  </UCard>
</template>

<script setup></script>

<style scoped></style>
