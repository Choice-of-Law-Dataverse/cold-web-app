<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <UCard class="cold-ucard">
          <div class="popular-searches-container flex flex-col gap-8">
            <!-- Title Section -->
            <div>
              <h2 class="popular-title text-left md:whitespace-nowrap">
                Link to Country Report
              </h2>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </main>
</template>

<script setup></script>

<style scoped>
.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem; /* Adjust spacing between buttons */
}

.suggestion-button {
  max-width: 100%; /* Ensure the button doesn’t overflow */
  white-space: normal; /* Allow text wrapping */
  text-align: left; /* Align text to the left */
  padding: 0.5rem 1rem; /* Adjust padding for better fit */
  word-break: break-word; /* Break long words */
}
</style>
