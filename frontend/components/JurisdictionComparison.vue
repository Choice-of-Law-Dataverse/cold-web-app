<template>
  <div class="col-span-12">
    <UCard class="cold-ucard">
      <UTable class="styled-table" :rows="people" />
    </UCard>
  </div>
</template>

<script setup lang="ts">
const people = [
  {
    theme: 'Preamble',
    question:
      'Is there a codification on choice of law or are there similar established rules?',
    jurisdiction: 'Yes',
  },
  {
    theme: 'Preamble',
    question: 'Are these rules part of a private international law instrument?',
    jurisdiction: 'Yes',
  },
  {
    theme: 'Preamble',
    question: 'Are these rules a consequence of a recent law reform?',
    jurisdiction: 'No',
  },
]
</script>

<style scoped>
/* Set the row height for all table rows */
.cold-ucard ::v-deep(tbody tr) {
  height: 74px; /* Ensure all rows are 74px high */
}

/* Set the row height for all header rows */
.cold-ucard ::v-deep(thead tr) {
  height: 52px; /* Set the header row height */
}

/* Target deep child classes inside UCard to remove padding */
.cold-ucard ::v-deep(.sm\:p-6) {
  padding: 0 !important;
}

.cold-ucard ::v-deep(.py-5) {
  padding: 0 !important;
}

.cold-ucard ::v-deep(.px-4) {
  padding: 0 !important;
}

/* Ensure the table spans the full width of the card */
.cold-ucard {
  padding: 0; /* Remove padding from UCard */
}

.table-wrapper {
  width: 100%; /* Ensure the table spans the full width of the wrapper */
  overflow-x: auto; /* Handle horizontal scrolling if needed */
}

/* Styling the table rows to indent text on left and right */
.styled-table ::v-deep(tbody tr td),
.styled-table ::v-deep(thead tr th) {
  text-indent: 32px; /* Indent text on the left */
  position: relative; /* Make sure the pseudo-element aligns properly */
}

/* Add indentation for the right side using a pseudo-element */
.styled-table ::v-deep(tbody tr td::after),
.styled-table ::v-deep(thead tr th::after) {
  content: ''; /* Empty content for pseudo-element */
  display: block;
  width: 32px; /* Create space on the right */
  position: absolute;
  right: 0;
  height: 100%;
}
</style>
