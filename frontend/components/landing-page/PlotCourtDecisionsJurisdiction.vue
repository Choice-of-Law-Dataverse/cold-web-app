<template>
  <UCard class="cold-ucard">
    <h2 class="popular-title">Top 10 Jurisdictions by Court Decisions</h2>
    <p class="result-value-small">
      Click bars to see a jurisdiction's decisions
    </p>
    <div ref="plotlyContainer"></div>
    <div v-if="isLoading" class="loading-state"><LoadingLandingPageCard /></div>
  </UCard>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import LoadingLandingPageCard from '../layout/LoadingLandingPageCard.vue'

const chartData = ref(null)
const chartLayout = ref(null)
const chartConfig = ref(null)

const plotlyContainer = ref(null)

const isLoading = ref(true)

onMounted(async () => {
  // Dynamically import Plotly only on the client
  const Plotly = await import('plotly.js-dist-min')

  // Fetch JSON data
  const response = await fetch('count_jurisdictions.json')
  const jurisdictionData = await response.json()

  // Transform the JSON data for Plotly
  const xValues = jurisdictionData.map((item) => item.n) // Extract 'n' values
  const yValues = jurisdictionData.map((item) => item.jurisdiction) // Extract 'Jurisdiction.Names'
  const links = jurisdictionData.map((item) => item.url) // Extract URLs (add this to your JSON)

  // Fetch the Tailwind color from CSS variables
  const coldGreen = getComputedStyle(document.documentElement)
    .getPropertyValue('--color-cold-green')
    .trim()

  const coldGreenAlpha = getComputedStyle(document.documentElement)
    .getPropertyValue('--color-cold-green-alpha')
    .trim()

  const coldGray = getComputedStyle(document.documentElement)
    .getPropertyValue('--color-cold-gray')
    .trim()

  const coldNight = getComputedStyle(document.documentElement)
    .getPropertyValue('--color-cold-night')
    .trim()

  // Initialize the colors for the bars
  const initialColors = Array(xValues.length).fill(coldGreen)

  // Define the bar chart data
  chartData.value = [
    {
      x: xValues, // Use the 'n' values for x-axis
      y: yValues, // Use the 'Jurisdiction.Names' for y-axis
      type: 'bar', // Specify bar chart
      orientation: 'h', // Specify horizontal orientation
      marker: {
        color: [...initialColors], // Apply initial colors
      },
      customdata: links, // Add URLs to customdata
      hoverinfo: 'none',
    },
  ]

  // Define the layout for the chart
  chartLayout.value = {
    dragmode: false, // Disable drag to zoom
    bargap: 0.5, // Adjust spacing between bars (smaller value = thicker bars)
    height: chartData.value[0].y.length * 35, // Dynamically adjust chart height for y-axis labels
    margin: {
      l: 200, // Increase left margin to accommodate long country names
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
      size: 14,
      color: coldNight,
    },
  }

  // Define the chart configuration
  chartConfig.value = {
    scrollZoom: false, // Disable zooming
    displayModeBar: false, // Hide the toolbar
    staticPlot: false, // Keep interactivity except zoom
    responsive: true, // Ensure responsiveness
  }

  // Render the chart
  if (plotlyContainer.value) {
    const plot = await Plotly.newPlot(
      plotlyContainer.value,
      chartData.value,
      chartLayout.value,
      chartConfig.value
    )

    // Get the drag layer for pointer adjustments
    const dragLayer = document.getElementsByClassName('nsewdrag')[0]

    // Add hover effect to change bar color
    // Add hover effect to change the pointer style
    plot.on('plotly_hover', function (data) {
      if (dragLayer) {
        dragLayer.style.cursor = 'pointer' // Change cursor to pointer
      }
      // Change bar color on hover
      const colors = [...data.points[0].data.marker.color] // Copy current colors
      const pointIndex = data.points[0].pointNumber // Index of the hovered bar
      colors[pointIndex] = coldGreenAlpha // Set the hover color for the specific bar
      const update = { 'marker.color': [colors] } // Create the update payload
      Plotly.restyle(plotlyContainer.value, update) // Apply the hover color
    })

    // Reset pointer style on unhover
    plot.on('plotly_unhover', function () {
      if (dragLayer) {
        dragLayer.style.cursor = 'default' // Reset cursor to default
      }
      // Reset bar colors on unhover
      const update = { 'marker.color': [initialColors] } // Reset to initial colors
      Plotly.restyle(plotlyContainer.value, update)
    })

    // Add click event for navigation
    plot.on('plotly_click', (data) => {
      const clickedUrl = data.points[0].customdata
      if (clickedUrl) {
        window.location.href = clickedUrl
      }
    })

    // Update loading state
    isLoading.value = false
  } else {
    console.error('Plotly container is not ready')
  }
})
</script>

<style scoped>
.result-value-small {
  line-height: 36px !important;
}
</style>
