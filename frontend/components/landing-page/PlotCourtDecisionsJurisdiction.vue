<template>
  <UCard class="cold-ucard flex h-full w-full flex-col">
    <h2 class="popular-title">Court Decisions by Jurisdiction</h2>
    <p class="result-value-small">
      Click bars to see a jurisdiction's decisions
    </p>

    <div v-if="isLoading" class="loading-state">
      <LoadingLandingPageCard />
    </div>

    <div v-else-if="data && chartData.length > 0" class="chart-container">
      <div class="chart-bars">
        <div
          v-for="(item, index) in chartData"
          :key="index"
          class="bar-row"
          @click="handleBarClick(item.url)"
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
              <span class="bar-value">{{ item.count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { ref, computed } from "vue";
import LoadingLandingPageCard from "@/components/layout/LoadingLandingPageCard.vue";
import { useJurisdictionChart } from "@/composables/useJurisdictionChart";
import { navigateTo } from "#app";

const { data, isLoading } = useJurisdictionChart();
const hoveredIndex = ref(-1);

// Process the data for our simple chart
const chartData = computed(() => {
  if (!data.value) return [];

  const { xValues, yValues, links } = data.value;
  const maxValue = Math.max(...xValues);

  return xValues.map((count, index) => ({
    jurisdiction: yValues[index],
    count,
    percentage: (count / maxValue) * 100,
    url: links[index],
  }));
});

// Handle bar click navigation
function handleBarClick(url) {
  if (url) {
    navigateTo(url);
  }
}

// Handle bar hover effects
function handleBarHover(index, isHovering) {
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
  gap: 1rem;
}

.bar-row {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.bar-row:hover {
  opacity: 0.9;
}

.bar-label {
  min-width: 150px;
  text-align: right;
  padding-right: 1rem;
  font-size: 0.9rem;
  color: var(--color-cold-night, #1e293b);
}

.bar-container {
  flex: 1;
  height: 32px;
  position: relative;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 100%;
  background: var(--color-cold-green, #10b981);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 0.75rem;
  border-radius: 4px;
  position: relative;
}

.bar-hovered {
  background: var(--color-cold-green-alpha, #059669);
  transform: scaleY(1.05);
}

.bar-value {
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
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
    padding-right: 0.5rem;
  }
}
</style>
