<template>
  <div
    ref="rootEl"
    class="base-legal-content"
    :class="{ 'is-first': isFirstProvision }"
  >
    <div v-if="error">{{ error }}</div>
    <div v-else :id="anchorId" :class="['legal-content', customClass]">
      <div class="mb-4 flex flex-col">
        <div class="flex items-start justify-between gap-2">
          <a
            :href="`#${anchorId}`"
            class="label-key-provision-article anchor min-w-0 flex-1"
            @click="toggleOpen"
          >
            {{ displayTitle }}
          </a>

          <button
            type="button"
            :aria-controls="`${anchorId}-content`"
            :aria-expanded="isOpen.toString()"
            :aria-label="isOpen ? 'Collapse content' : 'Expand content'"
            class="flex-shrink-0"
            @click="toggleOpen"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              width="16"
              height="16"
              fill="none"
              :style="{
                color: 'var(--color-cold-teal)',
                transform: isOpen ? 'rotate(90deg)' : 'rotate(0deg)',
              }"
            >
              <path
                d="M9 6l6 6-6 6"
                stroke="currentColor"
                stroke-width="3"
                stroke-linecap="square"
                stroke-linejoin="square"
              />
            </svg>
          </button>
        </div>

        <div v-if="isOpen" class="mt-2 flex justify-end">
          <slot name="header-actions" />
        </div>

        <div
          v-show="isOpen"
          :id="`${anchorId}-content`"
          class="content-body prose"
        >
          <slot />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from "vue";

const props = defineProps({
  title: {
    type: String,
    required: false,
    default: "Loading...",
  },
  anchorId: {
    type: String,
    required: true,
  },
  class: {
    type: String,
    default: "",
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: null,
  },
});

const customClass = computed(() => props.class || "");
const displayTitle = computed(() => (props.loading ? "" : props.title || ""));

const isOpen = ref(false);
const toggleOpen = () => {
  isOpen.value = !isOpen.value;
};

const rootEl = ref(null);
const isFirstProvision = ref(false);
const evaluateIsFirst = () => {
  const el = rootEl.value;
  const parent = el?.parentElement;
  if (!el || !parent) {
    isFirstProvision.value = false;
    return;
  }
  const firstBase = parent.querySelector(".base-legal-content");
  isFirstProvision.value = firstBase === el;
};

const scrollToAnchor = async () => {
  const hash = window.location.hash.slice(1);
  if (hash === props.anchorId) {
    // If navigated directly via hash, auto-expand for visibility
    isOpen.value = true;
    await nextTick();
    const anchorElement = document.getElementById(hash);
    if (anchorElement) {
      anchorElement.scrollIntoView({ behavior: "smooth" });
    }
  }
};

onMounted(() => {
  evaluateIsFirst();
  scrollToAnchor();
});
</script>

<style scoped>
.anchor {
  text-decoration: none;
  color: var(--color-cold-night) !important;
  display: block;
  margin-top: 50px;
}

.base-legal-content.is-first .anchor {
  margin-top: 0;
}

.content-body {
  font-size: 14px !important;
  font-weight: 400 !important;
  white-space: pre-line;
  word-wrap: break-word;
  word-break: break-word;
}

/* Add spacing between provision component instances */
.base-legal-content {
  margin-top: 16px; /* default spacing between items */
}
</style>
