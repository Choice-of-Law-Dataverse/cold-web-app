<template>
  <UCard>
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

<script setup lang="ts">
import SectionNav from "@/components/layout/SectionNav.vue";

interface NavLink {
  label: string;
  key: string;
  path: string;
}

interface Props {
  navLinks?: NavLink[] | null;
  enableHierarchicalNumbering?: boolean;
}

withDefaults(defineProps<Props>(), {
  navLinks: null,
  enableHierarchicalNumbering: false,
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
    padding-inline-start: 0px;
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

<style>
@reference "tailwindcss";

.content-page-prose h1,
.content-page-prose h2,
.content-page-prose h3 {
  @apply mt-8 mb-4;
}

.content-page-prose h1 {
  @apply mt-0;
}

.content-page-prose a {
  @apply text-cold-purple;
}

.content-page-prose a:hover {
  color: color-mix(in srgb, var(--color-cold-purple) 85%, #000);
}

.content-page-prose a:focus-visible {
  @apply outline-cold-purple rounded-sm outline-2 outline-offset-2;
}

.content-page-prose ul,
.content-page-prose ol {
  @apply my-4 pl-6;
}

.content-page-prose ul {
  @apply list-disc;
}

.content-page-prose ol {
  @apply list-decimal;
}

.content-page-prose li {
  @apply mb-2;
}

.content-page-prose code {
  @apply text-cold-night rounded-sm bg-gray-50 px-1.5 py-0.5 text-[0.9em];
}

.content-page-prose pre {
  @apply overflow-x-auto rounded-lg border border-gray-200 bg-gray-50 p-4;
}

.content-page-prose pre code {
  @apply bg-transparent p-0;
}

.content-page-prose blockquote {
  @apply border-l-[3px] border-gray-200 pl-4 text-gray-600 italic;
}

.content-page-prose table {
  @apply my-6 w-full border-collapse;
}

.content-page-prose th {
  @apply border-b-2 border-gray-200 bg-gray-50 p-3 text-left font-semibold;
}

.content-page-prose td {
  @apply border-b border-gray-200 p-3;
}

.content-page-prose p {
  @apply mb-5;
}

.content-page-prose img {
  @apply my-4 h-auto max-w-full;
}

.external-link-icon {
  @apply ml-[0.25em] inline-block h-[1em] w-[1em] align-middle;
}
</style>
