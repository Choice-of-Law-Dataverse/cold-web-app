<template>
  <UCard class="cold-ucard gradient-top-border flex h-full w-full flex-col">
    <h2 class="card-title">Court Decisions by Jurisdiction</h2>
    <p class="card-subtitle">
      Explore countries with the highest case law volume
    </p>

    <div v-if="isLoading" class="loading-state">
      <LoadingLandingPageCard />
    </div>

    <div v-else-if="data && chartData.length > 0" class="chart-container">
      <div class="chart-bars">
        <NuxtLink
          v-for="(item, index) in chartData"
          :key="index"
          :to="item.url"
          class="bar-row hover-row no-underline"
          @mouseenter="() => handleBarHover(index, true)"
          @mouseleave="() => handleBarHover(index, false)"
        >
          <div class="bar-label">{{ item.jurisdiction }}</div>
          <div class="bar-container">
            <div
              class="bar"
              :class="{ 'bar-hovered': hoveredIndex === index }"
              :style="{ width: item.percentage + '%' }"
            >
              <img
                v-if="item.flagUrl"
                :src="item.flagUrl"
                :alt="item.jurisdiction"
                class="bar-flag"
              />
              <span class="bar-value">{{ item.count }}</span>
            </div>
          </div>
        </NuxtLink>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import LoadingLandingPageCard from "@/components/layout/LoadingLandingPageCard.vue";
import {
  useJurisdictionChart,
  useJurisdictions,
} from "@/composables/useJurisdictions";

const { data, isLoading } = useJurisdictionChart();
const { data: jurisdictions } = useJurisdictions();
const hoveredIndex = ref(-1);

const jurisdictionLookup = computed(() => {
  if (!jurisdictions.value) return new Map<string, string>();
  const lookup = new Map<string, string>();
  for (const j of jurisdictions.value) {
    if (j.alpha3Code) {
      lookup.set(j.Name.toLowerCase(), j.alpha3Code.toLowerCase());
    }
  }
  return lookup;
});

function getFlagUrl(jurisdictionName: string) {
  const alpha3 = jurisdictionLookup.value.get(jurisdictionName.toLowerCase());
  if (!alpha3) return null;
  return `https://choiceoflaw.blob.core.windows.net/assets/flags/${alpha3}.svg`;
}

const chartData = computed(() => {
  if (!data.value) return [];

  const { xValues, yValues, links } = data.value;
  const maxValue = Math.max(...xValues);

  return xValues.map((count, index) => ({
    jurisdiction: yValues[index],
    count,
    percentage: (count / maxValue) * 100,
    url: links[index],
    flagUrl: getFlagUrl(yValues[index]),
  }));
});

function handleBarHover(index: number, isHovering: boolean) {
  hoveredIndex.value = isHovering ? index : -1;
}
</script>

<style scoped>
.chart-container {
  padding: 1rem 0;
}

.chart-bars {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.bar-row {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0.5rem;
  margin: 0 -0.5rem;
}

.bar-label {
  min-width: 150px;
  text-align: right;
  padding-right: 1rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-cold-night);
}

.bar-container {
  flex: 1;
  height: 32px;
  position: relative;
  background: rgb(241 245 249);
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 100%;
  background: linear-gradient(
    90deg,
    color-mix(in srgb, var(--color-cold-purple) 15%, rgb(241 245 249)),
    color-mix(in srgb, var(--color-cold-green) 12%, rgb(241 245 249))
  );
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0.75rem;
  border-radius: 4px;
  position: relative;
}

.bar-flag {
  height: 18px;
  width: auto;
  border-radius: 2px;
  flex-shrink: 0;
}

.bar-hovered {
  background: linear-gradient(
    90deg,
    color-mix(in srgb, var(--color-cold-purple) 25%, rgb(241 245 249)),
    color-mix(in srgb, var(--color-cold-green) 20%, rgb(241 245 249))
  );
}

.bar-value {
  color: var(--color-cold-night);
  font-weight: 600;
  font-size: 0.875rem;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .bar-label {
    min-width: 120px;
    font-size: 0.8rem;
  }

  .bar-container {
    height: 28px;
  }

  .bar-value {
    font-size: 0.8rem;
  }

  .bar-flag {
    height: 14px;
  }
}
</style>
