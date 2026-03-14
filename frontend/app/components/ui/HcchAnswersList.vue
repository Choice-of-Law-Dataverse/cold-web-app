<template>
  <UCard
    :ui="{
      body: '!p-0',
      header: 'border-b-0 px-6 py-5',
    }"
  >
    <template #header>
      <h3 class="comparison-title">HCCH Questions &amp; Answers</h3>
    </template>
    <div class="gradient-top-border" />
    <ul class="hcch-list">
      <li v-for="answer in answers" :key="answer.id" class="hcch-item">
        <EntityLink
          :id="answer.coldId || String(answer.id)"
          :title="answer.adaptedQuestion || 'Question'"
          base-path="/hcch-answer"
        >
          <span class="hcch-question">{{
            answer.adaptedQuestion || "Question"
          }}</span>
          <span v-if="answer.position" class="hcch-position">{{
            answer.position
          }}</span>
        </EntityLink>
      </li>
    </ul>
  </UCard>
</template>

<script setup lang="ts">
import EntityLink from "@/components/ui/EntityLink.vue";

defineProps<{
  answers: {
    id: number;
    coldId?: string | null;
    adaptedQuestion?: string | null;
    position?: string | null;
  }[];
}>();
</script>

<style scoped>
.hcch-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.hcch-item {
  border-bottom: 1px solid var(--ui-border);
}

.hcch-item:last-child {
  border-bottom: none;
}

.hcch-item :deep(.entity-link),
.hcch-item :deep(a) {
  display: flex;
  align-items: baseline;
  gap: 2rem;
  padding: 1rem 1.5rem;
  text-decoration: none;
  color: inherit;
  transition: background 0.15s ease;
}

.hcch-item :deep(.entity-link:hover),
.hcch-item :deep(a:hover) {
  background: linear-gradient(
    315deg,
    color-mix(in srgb, var(--color-cold-purple) 2%, white),
    color-mix(in srgb, var(--color-cold-green) 1%, white)
  );
}

.hcch-question {
  flex: 1;
  font-size: 0.9375rem;
  color: var(--color-cold-night);
}

.hcch-position {
  flex-shrink: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-cold-night);
}
</style>
