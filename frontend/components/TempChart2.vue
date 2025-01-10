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

  // Fetch JSON data
  const response = await fetch('count_jurisdictions.json')
  const jurisdictionData = await response.json()

  // Transform the JSON data for Plotly
  const xValues = jurisdictionData.map((item) => item.n) // Extract 'n' values
  const yValues = jurisdictionData.map((item) => item.jurisdiction) // Extract 'Jurisdiction.Names'

  // Fetch the Tailwind color from CSS variables
  const coldGreen = getComputedStyle(document.documentElement)
    .getPropertyValue('--color-cold-green')
    .trim()

  // Define the bar chart data
  chartData.value = [
    {
      x: xValues, // Use the 'n' values for x-axis
      y: yValues, // Use the 'Jurisdiction.Names' for y-axis
      type: 'bar', // Specify bar chart
      orientation: 'h', // Specify horizontal orientation
      marker: {
        color: coldGreen, // Apply the Tailwind color
      },
    },
  ]

  // Define the layout for the chart
  chartLayout.value = {
    //title: 'Court Decisions by Jurisdiction', // Title of the chart
    //xaxis: { title: 'Count' }, // Label for x-axis
    //yaxis: { title: 'Animals' }, // Label for y-axis
    dragmode: false, // Disable drag to zoom
    bargap: 0.4, // Adjust spacing between bars (smaller value = thicker bars)
    height: chartData.value[0].y.length * 80, // Dynamically adjust chart height for y-axis labels
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
