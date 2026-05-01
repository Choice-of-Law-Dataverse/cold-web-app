<template>
  <div ref="wrapperRef" class="picker-wrapper">
    <button
      type="button"
      class="picker-trigger"
      :aria-expanded="isOpen"
      aria-haspopup="listbox"
      @click="isOpen = !isOpen"
    >
      <Icon name="i-material-symbols:public" class="picker-trigger-icon" />
      <span class="picker-trigger-label">Open a jurisdiction report</span>
      <Icon
        name="i-material-symbols:expand-more-rounded"
        class="picker-trigger-chevron"
        :class="{ 'picker-trigger-chevron--open': isOpen }"
      />
    </button>

    <Teleport to="body">
      <div v-if="isOpen" class="picker-overlay" @click.self="isOpen = false">
        <div ref="panelRef" class="picker-panel" :style="panelStyle">
          <UInput
            v-model="search"
            placeholder="Search a jurisdiction..."
            icon="i-material-symbols:search"
            autofocus
            variant="none"
            class="picker-search"
          />
          <div class="picker-list" role="listbox">
            <button
              v-for="item in filtered"
              :key="item.coldId || item.name"
              class="picker-item"
              type="button"
              role="option"
              :disabled="!hasCoverage(item.answerCoverage)"
              @click="selectItem(item)"
            >
              <JurisdictionFlag
                v-if="item.coldId"
                :iso3="item.coldId"
                :faded="!hasCoverage(item.answerCoverage)"
                class="picker-flag"
              />
              <span
                class="picker-item-label"
                :class="{
                  'picker-item-label--faded': !hasCoverage(item.answerCoverage),
                }"
              >
                {{ item.label }}
              </span>
            </button>
            <div v-if="filtered.length === 0" class="picker-empty">
              No jurisdictions found
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from "vue";
import { useRouter } from "#imports";
import {
  useJurisdictions,
  type ProcessedJurisdiction,
} from "@/composables/useJurisdictions";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";

const router = useRouter();
const { data: jurisdictions } = useJurisdictions();

const isOpen = ref(false);
const search = ref("");
const wrapperRef = ref<HTMLElement | null>(null);
const panelRef = ref<HTMLElement | null>(null);
const panelStyle = ref<Record<string, string>>({});

const hasCoverage = (coverage?: number) => (coverage ?? 0) > 0;

const filtered = computed(() => {
  const list = jurisdictions.value ?? [];
  const q = search.value.toLowerCase().trim();
  if (!q) return list;
  return list.filter((j) => j.label.toLowerCase().includes(q));
});

watch(isOpen, async (open) => {
  if (open) {
    await nextTick();
    positionPanel();
  } else {
    search.value = "";
  }
});

function positionPanel() {
  if (!wrapperRef.value) return;
  const rect = wrapperRef.value.getBoundingClientRect();
  const offset = 4;
  const collisionPadding = 8;
  const availableHeight =
    window.innerHeight - rect.bottom - offset - collisionPadding;
  panelStyle.value = {
    top: `${rect.bottom + offset}px`,
    left: `${rect.left}px`,
    minWidth: `${rect.width}px`,
    maxHeight: `${availableHeight}px`,
  };
}

async function selectItem(item: ProcessedJurisdiction) {
  if (!hasCoverage(item.answerCoverage) || !item.coldId) return;
  isOpen.value = false;
  await router.push(`/jurisdiction/${item.coldId.toUpperCase()}`);
}
</script>

<style scoped>
.picker-wrapper {
  position: relative;
}

.picker-trigger {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem 0.5rem 0.875rem;
  background: white;
  border: 1px solid color-mix(in srgb, var(--color-cold-night) 12%, transparent);
  border-radius: 0.5rem;
  cursor: pointer;
  font-family: "DM Sans", sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-cold-night);
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.04);
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease;
}

.picker-trigger:hover {
  border-color: color-mix(in srgb, var(--color-cold-purple) 35%, transparent);
  box-shadow: 0 2px 6px -2px rgb(0 0 0 / 0.08);
}

.picker-trigger:focus-visible {
  outline: 2px solid var(--color-cold-purple);
  outline-offset: 2px;
}

.picker-trigger-icon {
  flex-shrink: 0;
  font-size: 1rem;
  color: var(--color-cold-purple);
}

.picker-trigger-label {
  white-space: nowrap;
}

.picker-trigger-chevron {
  flex-shrink: 0;
  font-size: 1rem;
  color: color-mix(in srgb, var(--color-cold-night) 50%, transparent);
  transition: transform 0.2s ease;
}

.picker-trigger-chevron--open {
  transform: rotate(180deg);
}

@media (max-width: 480px) {
  .picker-trigger {
    padding: 0.4375rem 0.625rem 0.4375rem 0.75rem;
    font-size: 0.8125rem;
  }
  .picker-trigger-label {
    max-width: 11rem;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.picker-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
}

.picker-panel {
  position: fixed;
  width: 320px;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 0.625rem;
  border: 1px solid var(--color-cold-gray);
  box-shadow:
    0 12px 32px -12px rgb(0 0 0 / 0.18),
    0 4px 12px -6px rgb(0 0 0 / 0.08);
  z-index: 101;
  overflow: hidden;
}

.picker-search {
  border-bottom: 1px solid var(--color-cold-gray);
}

.picker-search :deep(input) {
  text-align: left;
}

.picker-list {
  overflow-y: auto;
  padding: 0.25rem;
}

.picker-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.625rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-family: "DM Sans", sans-serif;
  color: var(--color-cold-night);
  text-align: left;
  cursor: pointer;
  transition: background 0.1s ease;
  border: none;
  background: none;
}

.picker-item:hover:not(:disabled) {
  background: var(--gradient-subtle-hover);
}

.picker-item:disabled {
  cursor: not-allowed;
}

.picker-item-label--faded {
  color: var(--color-cold-slate);
}

.picker-flag {
  flex-shrink: 0;
}

.picker-empty {
  padding: 1rem;
  text-align: center;
  font-size: 0.875rem;
  color: var(--color-cold-slate);
}
</style>
