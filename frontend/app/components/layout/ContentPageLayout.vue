<template>
  <UCard class="cold-ucard">
    <div class="px-6 pt-6">
      <SectionNav v-if="navLinks" :links="navLinks" />
      <SectionNav v-else />
    </div>
    <!-- Main Content -->
    <div
      class="content-page-prose prose max-w-none px-6 py-8"
      :class="{ 'hierarchical-numbering': enableHierarchicalNumbering }"
    >
      <slot />
    </div>
  </UCard>
</template>

<script setup>
import SectionNav from "@/components/layout/SectionNav.vue";

defineProps({
  navLinks: {
    type: Array,
    default: null,
    required: false,
  },
  enableHierarchicalNumbering: {
    type: Boolean,
    default: false,
  },
});
</script>

<style scoped>
/* Hierarchical numbering styles - only applied when prop is true */
.hierarchical-numbering {
  /* Initialize the counter once at the container level */
  counter-reset: list-counter;

  /* Add consistent spacing between list items */
  ::v-deep(ol > li),
  ::v-deep(ol ol > li),
  ::v-deep(ol ol ol > li) {
    margin-bottom: 24px;
  }

  /* Don't reset the counter for each list */
  ::v-deep(ol) {
    list-style: none;
    margin-left: 0;
    padding-left: 0;
  }

  ::v-deep(ol > li) {
    counter-increment: list-counter;
    padding-inline-start: 0px !important;
  }

  ::v-deep(ol > li::before) {
    content: counter(list-counter) "";
    font-weight: bold;
    padding-right: 1em;
  }

  ::v-deep(ol ol) {
    counter-reset: sub-list-counter;
    list-style: none;
    margin-left: 24px;
  }

  ::v-deep(ol ol > li) {
    counter-increment: sub-list-counter;
  }

  ::v-deep(ol ol > li::before) {
    content: counter(list-counter) "." counter(sub-list-counter) "";
    font-weight: bold;
  }

  ::v-deep(ol ol ol) {
    counter-reset: sub-sub-list-counter;
    list-style: none;
    margin-left: 24px;
  }

  ::v-deep(ol ol ol > li) {
    counter-increment: sub-sub-list-counter;
  }

  ::v-deep(ol ol ol > li::before) {
    content: counter(list-counter) "." counter(sub-list-counter) "."
      counter(sub-sub-list-counter) "";
    font-weight: bold;
  }
}
</style>
