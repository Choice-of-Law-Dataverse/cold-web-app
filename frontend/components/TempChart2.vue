<template>
  <UCard class="cold-ucard">
    <h2 class="popular-title">Court Decisions by Jurisdiction</h2>
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

  // Define the bar chart data
  chartData.value = [
    {
      x: [20, 14, 23], // Values on the x-axis for horizontal bar chart
      y: ['Giraffes', 'Orangutans', 'Monkeys'], // Categories on the y-axis
      type: 'bar', // Specify bar chart
      orientation: 'h', // Specify horizontal orientation
    },
  ]

  // Define the layout for the chart
  chartLayout.value = {
    //title: 'Court Decisions by Jurisdiction', // Title of the chart
    //xaxis: { title: 'Count' }, // Label for x-axis
    //yaxis: { title: 'Animals' }, // Label for y-axis
    dragmode: false, // Disable drag to zoom
  }

  // Define the chart configuration
  chartConfig.value = {
    scrollZoom: false, // Disable zooming
    displayModeBar: false, // Hide the toolbar
    staticPlot: true, // Keep interactivity except zoom
    responsive: true, // Ensure responsiveness
  }

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
