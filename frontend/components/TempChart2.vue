<template>
  <UCard class="cold-ucard">
    <div ref="plotlyContainer"></div>
  </UCard>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const chartData = ref(null)
const chartLayout = ref(null)
const chartConfig = ref(null)

const plotlyContainer = ref(null)

onMounted(async () => {
  // Dynamically import Plotly only on the client
  const Plotly = await import('plotly.js-dist-min')

  chartData.value = [
    {
      x: [1, 2, 3, 4, 5],
      y: [10, 15, 13, 17, 21],
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: 'red' },
    },
  ]
  chartLayout.value = { title: 'Sample Plot' }
  chartConfig.value = { responsive: true }

  if (plotlyContainer.value) {
    Plotly.newPlot(
      plotlyContainer.value,
      chartData.value,
      chartLayout.value,
      chartConfig.value
    )
  } else {
    console.error('Plotly container is not ready')
  }
})
</script>
