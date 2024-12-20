<template>
  <UCard class="cold-ucard">
    <div>
      <h2 class="popular-title">Court Decisions by Jurisdiction</h2>
      <client-only>
        <nuxt-plotly
          v-if="isColorLoaded"
          :data="data"
          :layout="layout"
          :config="config"
          style="width: 100%"
        ></nuxt-plotly>
      </client-only>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NuxtPlotlyConfig, NuxtPlotlyData, NuxtPlotlyLayout } from 'nuxt-plotly' // https://nuxt.com/modules/nuxt-plotly

// Reactive variable for the resolved color and render flag
const coldGreen = ref('')
const isColorLoaded = ref(false)

onMounted(() => {
  coldGreen.value = getComputedStyle(document.documentElement)
    .getPropertyValue('--color-cold-green')
    .trim()

  // Once the color is resolved, set the flag
  isColorLoaded.value = true
})

// Chart data (color initially empty)
const data = ref([
  {
    y: ['giraffes', 'orangutans', 'monkeys'],
    x: [20, 14, 23],
    type: 'bar',
    orientation: 'h',
    marker: { color: coldGreen.value },
  },
])

// Watch for color changes and update data
watch(coldGreen, (newColor) => {
  data.value[0].marker.color = newColor
})

const layout = {
  title: 'Court Decisions by Jurisdiction',
  xaxis: { title: 'Count' },
  yaxis: { title: 'Animals' },
}

// Define the bar chart data
// const data = [
//   {
//     y: ['giraffes', 'orangutans', 'monkeys'],
//     x: [20, 14, 23],
//     type: 'bar',
//     orientation: 'h',
//     marker: { color: coldGreen }, // Use the reactive variable
//   },
// ]

// Define the layout for the chart
// const layout: NuxtPlotlyLayout = {
//   //title: 'Court Decisions by Jurisdiction', // Title of the chart
//   //xaxis: { title: 'Animals' }, // Label for x-axis
//   //yaxis: { title: 'Count' }, // Label for y-axis
//   dragmode: false, // Disable drag to zoom
// }

// Optional configuration
const config: NuxtPlotlyConfig = {
  scrollZoom: false, // Allow zooming
  displayModeBar: false, // Hide the toolbar
  staticPlot: true, // Keep interactivity except zoom
}
</script>
