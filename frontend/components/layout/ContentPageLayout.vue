<template>
  <main class="px-6">
    <div class="mx-auto w-full max-w-container">
      <UCard class="cold-ucard">
        <SectionNav v-if="navLinks" :links="navLinks" />
        <SectionNav v-else />
        <!-- Main Content -->
        <div
          class="main-content prose flex w-full flex-col gap-12 -space-y-10 px-6"
          :class="{ 'hierarchical-numbering': enableHierarchicalNumbering }"
        >
          <slot />
        </div>
      </UCard>
    </div>
  </main>
</template>

<script setup>
import SectionNav from "@/components/layout/SectionNav.vue";

const _props = defineProps({
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
::v-deep(ul) {
  list-style-type: disc !important;
  padding-left: 12px !important;
}

/* Hierarchical numbering styles - only applied when prop is true */
.hierarchical-numbering {
  /* Add consistent spacing between list items */
  ::v-deep(ol > li),
  ::v-deep(ol ol > li),
  ::v-deep(ol ol ol > li),
  ::v-deep(ol ol ol ol > li) {
    margin-bottom: 24px !important;
  }

  /* Reset the counter for the top-level list */
  ::v-deep(ol) {
    counter-reset: list-counter;
    list-style: none !important;
    margin-left: 0;
    padding-left: 0;
  }

  ::v-deep(ol > li) {
    counter-increment: list-counter;
  }

  ::v-deep(ol > li::before) {
    content: counter(list-counter) ". ";
    font-weight: bold;
  }

  ::v-deep(ol ol) {
    counter-reset: sub-list-counter;
    list-style: none !important;
    margin-left: 24px;
  }

  ::v-deep(ol ol > li) {
    counter-increment: sub-list-counter;
  }

  ::v-deep(ol ol > li::before) {
    content: counter(list-counter) "." counter(sub-list-counter) ". ";
    font-weight: bold;
  }

  ::v-deep(ol ol ol) {
    counter-reset: sub-sub-list-counter;
    list-style: none !important;
    margin-left: 24px;
  }

  ::v-deep(ol ol ol > li) {
    counter-increment: sub-sub-list-counter;
  }

  ::v-deep(ol ol ol > li::before) {
    content: counter(list-counter) "." counter(sub-list-counter) "."
      counter(sub-sub-list-counter) ". ";
    font-weight: bold;
  }

  ::v-deep(ol ol ol ol) {
    counter-reset: sub-sub-sub-list-counter;
    list-style: none !important;
    margin-left: 24px;
  }

  ::v-deep(ol ol ol ol > li) {
    counter-increment: sub-sub-sub-list-counter;
  }

  ::v-deep(ol ol ol ol > li::before) {
    content: counter(list-counter) "." counter(sub-list-counter) "."
      counter(sub-sub-list-counter) "." counter(sub-sub-sub-list-counter) ". ";
    font-weight: bold;
  }
}
</style>
