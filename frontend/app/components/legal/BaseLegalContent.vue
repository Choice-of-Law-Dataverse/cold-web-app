<template>
  <div
    ref="rootEl"
    class="base-legal-content"
    :class="{ 'is-first': isFirstProvision, 'is-open': isOpen }"
  >
    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-else :id="anchorId" :class="['legal-content', customClass]">
      <button
        type="button"
        class="provision-header"
        :aria-controls="`${anchorId}-content`"
        :aria-expanded="isOpen.toString()"
        @click="toggleOpen"
      >
        <span class="provision-title">{{ displayTitle }}</span>
        <span class="provision-chevron" :class="{ 'is-open': isOpen }">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            width="18"
            height="18"
            fill="none"
          >
            <path
              d="M9 6l6 6-6 6"
              stroke="currentColor"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
      </button>

      <div
        v-show="isOpen"
        :id="`${anchorId}-content`"
        class="provision-content"
      >
        <div v-if="$slots['header-actions']" class="provision-actions">
          <slot name="header-actions" />
        </div>
        <p class="provision-body">
          <slot />
        </p>
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
.base-legal-content:not(.is-first) {
  margin-top: 8px;
}

.provision-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 4px 0;
  text-align: left;
  cursor: pointer;
  border: none;
  background: none;
}

.provision-title {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-cold-night);
  line-height: 1.5;
  text-decoration: underline;
  text-decoration-color: transparent;
  text-underline-offset: 2px;
  transition: text-decoration-color 0.15s ease;
}

.provision-header:hover .provision-title {
  text-decoration-color: var(--color-cold-purple);
}

.provision-chevron {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-cold-purple);
  opacity: 0.4;
  transition:
    transform 0.2s ease,
    opacity 0.15s ease;
}

.provision-header:hover .provision-chevron {
  opacity: 1;
}

.provision-chevron.is-open {
  transform: rotate(90deg);
  opacity: 0.7;
}

.provision-content {
  margin-top: 8px;
  padding: 12px 16px;
  background: color-mix(in srgb, var(--color-cold-gray) 40%, white);
  border-radius: 6px;
}

.provision-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.provision-body {
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.7;
  color: var(--color-cold-night);
  white-space: pre-line;
  word-wrap: break-word;
  word-break: break-word;
}

.error-message {
  padding: 4px 0;
  color: var(--color-label-court-decision);
  font-size: 0.875rem;
}
</style>
