<template>
  <div ref="wrapperRef" class="hero-picker-wrapper">
    <button class="hero-action" type="button" @click="isOpen = !isOpen">
      <Icon name="i-material-symbols:public" class="hero-action-icon" />
      <span>
        <span class="hero-action-title">Open a jurisdiction report</span>
        <span class="hero-action-desc"
          >Browse choice-of-law rules by jurisdiction</span
        >
      </span>
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
          <div class="picker-list">
            <button
              v-for="item in filtered"
              :key="item.coldId || item.name"
              class="picker-item"
              type="button"
              @click="selectItem(item)"
            >
              <JurisdictionFlag
                v-if="item.coldId"
                :iso3="item.coldId"
                :faded="!hasCoverage(item.answerCoverage)"
                class="picker-flag"
              />
              <span
                :style="{
                  color: hasCoverage(item.answerCoverage) ? undefined : 'gray',
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
import type { JurisdictionOption } from "@/types/analyzer";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";

const props = defineProps<{
  jurisdictions: JurisdictionOption[];
}>();

const emit = defineEmits<{
  (event: "jurisdiction-selected", value: JurisdictionOption | undefined): void;
}>();

const isOpen = ref(false);
const search = ref("");
const wrapperRef = ref<HTMLElement | null>(null);
const panelRef = ref<HTMLElement | null>(null);
const panelStyle = ref<Record<string, string>>({});

const hasCoverage = (coverage?: number) => (coverage ?? 0) > 0;

const filtered = computed(() => {
  const q = search.value.toLowerCase().trim();
  if (!q) return props.jurisdictions;
  return props.jurisdictions.filter((j) => j.label.toLowerCase().includes(q));
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
  panelStyle.value = {
    top: `${rect.bottom + 4}px`,
    left: `${rect.left}px`,
    minWidth: `${rect.width}px`,
  };
}

function selectItem(item: JurisdictionOption) {
  isOpen.value = false;
  emit("jurisdiction-selected", item);
}
</script>

<style scoped>
.hero-picker-wrapper {
  position: relative;
}

.hero-action {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  background: color-mix(in srgb, white 60%, transparent);
  text-decoration: none;
  transition: all 0.15s ease;
  cursor: pointer;
  width: 100%;
  border: none;
}

.hero-action:hover {
  background: white;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.06);
}

.hero-action-icon {
  flex-shrink: 0;
  font-size: 1.125rem;
  color: var(--color-cold-purple);
}

.hero-action-title {
  display: block;
  font-family: "DM Sans", sans-serif;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-cold-night);
  line-height: 1.3;
  text-align: left;
}

.hero-action-desc {
  display: block;
  font-family: "DM Sans", sans-serif;
  font-size: 0.6875rem;
  font-weight: 400;
  color: var(--color-cold-slate);
  line-height: 1.3;
  text-align: left;
}

.picker-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
}

.picker-panel {
  position: fixed;
  width: 300px;
  max-height: 360px;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 0.5rem;
  border: 1px solid var(--color-cold-gray);
  box-shadow:
    0 4px 12px rgb(0 0 0 / 0.08),
    0 1px 3px rgb(0 0 0 / 0.04);
  z-index: 101;
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

.picker-item:hover {
  background: var(--gradient-subtle-hover);
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
