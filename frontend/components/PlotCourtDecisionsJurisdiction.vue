<template>
  <UCard class="cold-ucard">
    <h2 class="popular-title">Court Decisions by Jurisdiction</h2>
    <p class="result-value-small">Top 10 Jurisdictions</p>
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

  const coldGray = getComputedStyle(document.documentElement)
    .getPropertyValue('--color-cold-gray')
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
    dragmode: false, // Disable drag to zoom
    bargap: 0.7, // Adjust spacing between bars (smaller value = thicker bars)
    height: chartData.value[0].y.length * 40, // Dynamically adjust chart height for y-axis labels
    margin: {
      l: 180, // Increase left margin to accommodate long country names
      r: 20, // Right margin
      t: 30, // Top margin
      b: 20, // Bottom margin
    },
    xaxis: {
      ticklen: 5, // Increase the length of the tick lines to create more space
      tickcolor: 'rgba(0,0,0,0)', // Make the tick lines transparent if you don't want them visible
      side: 'top', // Move x-axis labels to the top
      gridcolor: coldGray, // Use the Tailwind CSS color for gridlines
      zerolinecolor: coldGray, // Same color for the x-axis 0-value line
    },
    yaxis: {
      ticklen: 20, // Increase the length of the tick lines to create more space
      tickcolor: 'rgba(0,0,0,0)', // Make the tick lines transparent if you don't want them visible
    },
    font: {
      family: 'Inter, sans-serif', // Set the global font to Inter
    },
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
