<template>
  <UCard class="cold-ucard">
    <div>
      <h2 class="popular-title">Court Decisions by Jurisdiction</h2>
      <client-only>
        <nuxt-plotly
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
import { NuxtPlotlyConfig, NuxtPlotlyData, NuxtPlotlyLayout } from 'nuxt-plotly'

// Define the bar chart data
const data: NuxtPlotlyData = [
  {
    x: ['giraffes', 'orangutans', 'monkeys'], // Categories on the x-axis
    y: [20, 14, 23], // Values on the y-axis
    type: 'bar', // Specify bar chart
  },
]

// Define the layout for the chart
const layout: NuxtPlotlyLayout = {
  title: 'Court Decisions by Jurisdiction', // Title of the chart
  xaxis: { title: 'Animals' }, // Label for x-axis
  yaxis: { title: 'Count' }, // Label for y-axis
}

// Optional configuration
const config: NuxtPlotlyConfig = {
  scrollZoom: true, // Allow zooming
  displayModeBar: false, // Hide the toolbar
}
</script>
