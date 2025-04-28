<template>
  <main class="px-6">
    <div class="mx-auto w-full" style="max-width: var(--container-width)">
      <UCard class="cold-ucard">
        <SectionNav :links="learnNavLinks" />
        <!-- Main Content -->
        <div
          class="main-content prose -space-y-10 flex flex-col gap-12 px-6 w-full"
        >
          <ContentDoc path="/methodology_intro" />
          <ContentDoc path="/methodology_search" />
          <ContentDoc path="/methodology_questionnaire_intro" />
          <div class="questionnaire-wrapper">
            <ContentDoc path="/methodology_questionnaire" />
          </div>
        </div>
      </UCard>
    </div>
  </main>
</template>

<script setup>
import SectionNav from '~/components/layout/SectionNav.vue'
import { learnNavLinks } from '~/config/pageConfigs.js'
</script>

<style scoped>
::v-deep(ul) {
  list-style-type: disc !important;
  padding-left: 12px !important;
}

/* override Tailwind‑Typography’s default decimals */
::v-deep(.prose ol),
::v-deep(.prose ol ol) {
  list-style: none !important;
}

/* base <ol> numbering */
::v-deep(.prose ol) {
  counter-reset: item;
  padding-inline-start: 1rem !important;
}
::v-deep(.prose ol > li) {
  counter-increment: item;
  position: relative;
  padding-inline-start: 1rem !important;
}
::v-deep(.prose ol > li)::before {
  content: counter(item) '. ';
  position: absolute;
  left: 0;
}

/* nested <ol> numbering – e.g. “2.1. …” */
::v-deep(.prose ol ol) {
  counter-reset: subitem;
  padding-inline-start: 1rem !important;
}
::v-deep(.prose ol ol > li) {
  counter-increment: subitem;
  position: relative;
  padding-inline-start: 1.6rem !important;
}
::v-deep(.prose ol ol > li)::before {
  content: counter(item) '.' counter(subitem) '. ';
  position: absolute;
  left: 0;
}

/* third‐level nested <ol> – e.g. “1.1.1. …” */
::v-deep(.prose ol ol ol) {
  counter-reset: subsubitem;
  padding-inline-start: 1rem !important;
}
::v-deep(.prose ol ol ol > li) {
  counter-increment: subsubitem;
  position: relative;
  padding-inline-start: 2.6rem !important;
}
::v-deep(.prose ol ol ol > li)::before {
  content: counter(item) '.' counter(subitem) '.' counter(subsubitem) '. ';
  position: absolute;
  left: 0;
}

/* only apply continuous numbering inside our wrapper */
::v-deep(.questionnaire-wrapper .prose) {
  counter-reset: globalItem;
}

/* strip default bullets/numbers */
::v-deep(.questionnaire-wrapper .prose ul),
::v-deep(.questionnaire-wrapper .prose ol) {
  list-style: none !important;
  margin: 0;
  padding-left: 0;
}

/* top‑level items bump the global counter */
::v-deep(.questionnaire-wrapper .prose ol > li) {
  counter-increment: globalItem;
  position: relative;
  padding-inline-start: 1.5rem !important;
}
::v-deep(.questionnaire-wrapper .prose ol > li)::before {
  content: counter(globalItem) '. ';
  position: absolute;
  left: 0;
}

/* second‑level inside each top item */
::v-deep(.questionnaire-wrapper .prose ol > li > ol) {
  counter-reset: subitem;
  padding-inline-start: 1.5rem !important;
}
::v-deep(.questionnaire-wrapper .prose ol > li > ol > li) {
  counter-increment: subitem;
  position: relative;
  padding-inline-start: 1.5rem;
}
::v-deep(.questionnaire-wrapper .prose ol > li > ol > li)::before {
  content: counter(globalItem) '.' counter(subitem) '. ';
  position: absolute;
  left: 0;
}

/* third‑level nesting */
::v-deep(.questionnaire-wrapper .prose ol > li > ol > li > ol) {
  counter-reset: subsubitem;
  padding-inline-start: 1.5rem !important;
}
::v-deep(.questionnaire-wrapper .prose ol > li > ol > li > ol > li) {
  counter-increment: subsubitem;
  position: relative;
  padding-inline-start: 1.5rem;
}
::v-deep(.questionnaire-wrapper .prose ol > li > ol > li > ol > li)::before {
  content: counter(globalItem) '.' counter(subitem) '.' counter(subsubitem) '. ';
  position: absolute;
  left: 0;
}

/* Prevent any <ol> inside the wrapper from doing its own counter-reset */
::v-deep(.questionnaire-wrapper .prose ol),
::v-deep(.questionnaire-wrapper .prose ol ol),
::v-deep(.questionnaire-wrapper .prose ol ol ol) {
  counter-reset: none !important;
}

/* Now do exactly one reset for the whole doc */
::v-deep(.questionnaire-wrapper .prose) {
  counter-reset: globalItem;
}

/* strip default bullets/numbers */
::v-deep(.questionnaire-wrapper .prose ul),
::v-deep(.questionnaire-wrapper .prose ol) {
  list-style: none !important;
  margin: 0;
  padding-left: 0;
}

/* top‑level items bump the global counter */
::v-deep(.questionnaire-wrapper .prose ol > li) {
  counter-increment: globalItem;
  position: relative;
  padding-inline-start: 1.5rem !important;
}
::v-deep(.questionnaire-wrapper .prose ol > li)::before {
  content: counter(globalItem) '. ';
  position: absolute;
  left: 0;
}

/* second‑level inside each top item */
::v-deep(.questionnaire-wrapper .prose ol > li > ol) {
  counter-reset: subitem;
  padding-inline-start: 1.5rem !important;
}
::v-deep(.questionnaire-wrapper .prose ol > li > ol > li) {
  counter-increment: subitem;
  position: relative;
  padding-inline-start: 1.5rem;
}
::v-deep(.questionnaire-wrapper .prose ol > li > ol > li)::before {
  content: counter(globalItem) '.' counter(subitem) '. ';
  position: absolute;
  left: 0;
}

/* third‑level nesting */
::v-deep(.questionnaire-wrapper .prose ol > li > ol > li > ol) {
  counter-reset: subsubitem;
  padding-inline-start: 1.5rem !important;
}
::v-deep(.questionnaire-wrapper .prose ol > li > ol > li > ol > li) {
  counter-increment: subsubitem;
  position: relative;
  padding-inline-start: 1.5rem;
}
::v-deep(.questionnaire-wrapper .prose ol > li > ol > li > ol > li)::before {
  content: counter(globalItem) '.' counter(subitem) '.' counter(subsubitem) '. ';
  position: absolute;
  left: 0;
}

/* force all headings in the questionnaire back to flush left */
::v-deep(
  .questionnaire-wrapper .prose h1,
  .questionnaire-wrapper .prose h2,
  .questionnaire-wrapper .prose h3,
  .questionnaire-wrapper .prose h4,
  .questionnaire-wrapper .prose h5,
  .questionnaire-wrapper .prose h6
) {
  margin-left: -1.6rem !important;
  padding-left: 0 !important;
}
</style>
