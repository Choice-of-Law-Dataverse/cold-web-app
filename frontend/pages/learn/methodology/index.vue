<template>
  <main class="px-6">
    <div class="mx-auto w-full max-w-container">
      <UCard class="cold-ucard">
        <SectionNav :links="learnNavLinks" />
        <!-- Main Content -->
        <div
          class="main-content prose -space-y-10 flex flex-col gap-12 px-6 w-full"
        >
          <ContentDoc path="/methodology_intro" />
          <ContentDoc path="/methodology_questionnaire_intro" />
          <ContentDoc path="/methodology_questionnaire" />
        </div>
      </UCard>
    </div>
  </main>
</template>

<script setup>
import SectionNav from '@/components/layout/SectionNav.vue'
import { learnNavLinks } from '@/config/pageConfigs.js'
</script>

<style scoped>
::v-deep(ul) {
  list-style-type: disc !important;
  padding-left: 12px !important;
}

/* Add consistent spacing between list items */
::v-deep(ol > li),
::v-deep(ol ol > li),
::v-deep(ol ol ol > li),
::v-deep(ol ol ol ol > li) {
  margin-bottom: 24px !important; /* Adjust as needed for consistent spacing*/
}

/* Ensure sub-lists are indented without extra spacing */
::v-deep(ol ol),
::v-deep(ol ol ol),
::v-deep(ol ol ol ol) {
}

/* Reset the counter for the top-level list */
::v-deep(ol) {
  counter-reset: list-counter; /* Initialize the counter */
  list-style: none !important; /* Remove the default numbering */
  margin-left: 0;
  padding-left: 0;
}

::v-deep(ol > li) {
  counter-increment: list-counter; /* Increment the counter for each list item */
}

::v-deep(ol > li::before) {
  content: counter(list-counter) '. '; /* Display the counter number */
  font-weight: bold;
}

::v-deep(ol ol) {
  counter-reset: sub-list-counter; /* Reset the sub-list counter */
  list-style: none !important; /* Remove the default numbering */
  margin-left: 24px; /* Indent for sub-lists */
}

::v-deep(ol ol > li) {
  counter-increment: sub-list-counter; /* Increment the sub-list counter */
}

::v-deep(ol ol > li::before) {
  content: counter(list-counter) '.' counter(sub-list-counter) '. '; /* Display hierarchical numbering */
  font-weight: bold;
}

::v-deep(ol ol ol) {
  counter-reset: sub-sub-list-counter; /* Reset the sub-sub-list counter */
  list-style: none !important; /* Remove the default numbering */
  margin-left: 24px; /* Indent for sub-sub-lists */
}

::v-deep(ol ol ol > li) {
  counter-increment: sub-sub-list-counter; /* Increment the sub-sub-list counter */
}

::v-deep(ol ol ol > li::before) {
  content: counter(list-counter) '.' counter(sub-list-counter) '.'
    counter(sub-sub-list-counter) '. '; /* Display hierarchical numbering */
  font-weight: bold;
}

::v-deep(ol ol ol ol) {
  counter-reset: sub-sub-sub-list-counter; /* Reset the fourth-level counter */
  list-style: none !important; /* Remove the default numbering */
  margin-left: 24px; /* Indent for sub-sub-sub-lists */
}

::v-deep(ol ol ol ol > li) {
  counter-increment: sub-sub-sub-list-counter; /* Increment the fourth-level counter */
}

::v-deep(ol ol ol ol > li::before) {
  content: counter(list-counter) '.' counter(sub-list-counter) '.'
    counter(sub-sub-list-counter) '.' counter(sub-sub-sub-list-counter) '. '; /* Display hierarchical numbering */
  font-weight: bold;
}
</style>
