<template>
  <UCard class="cold-ucard">
    <h2 class="popular-title">Top 10 Jurisdictions by Court Decisions</h2>
    <p class="result-value-small">
      Click bars to see a jurisdiction's decisions
    </p>
    <div style="position: relative">
      <!-- Plotly container always rendered -->
      <div ref="plotlyContainer"></div>
      <!-- Overlay loading indicator -->
      <div
        v-if="isLoading"
        style="
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          display: flex;
          background: rgba(255, 255, 255, 0.75);
          z-index: 10;
        "
      >
        Loading...
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const chartData = ref(null)
const chartLayout = ref(null)
const chartConfig = ref(null)
const plotlyContainer = ref(null)
const isLoading = ref(true) // added loading state

onMounted(async () => {
  try {
    const Plotly = await import('plotly.js-dist-min')
    const response = await fetch('count_jurisdictions.json')
    const jurisdictionData = await response.json()

    const xValues = jurisdictionData.map((item) => item.n)
    const yValues = jurisdictionData.map((item) => item.jurisdiction)
    const links = jurisdictionData.map((item) => item.url)

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

    const initialColors = Array(xValues.length).fill(coldGreen)

    chartData.value = [
      {
        x: xValues,
        y: yValues,
        type: 'bar',
        orientation: 'h',
        marker: {
          color: [...initialColors],
        },
        customdata: links,
        hoverinfo: 'none',
      },
    ]

    chartLayout.value = {
      dragmode: false,
      bargap: 0.5,
      height: chartData.value[0].y.length * 35,
      margin: {
        l: 200,
        r: 20,
        t: 30,
        b: 20,
      },
      xaxis: {
        ticklen: 5,
        tickcolor: 'rgba(0,0,0,0)',
        side: 'top',
        gridcolor: coldGray,
        zerolinecolor: coldGray,
      },
      yaxis: {
        ticklen: 20,
        tickcolor: 'rgba(0,0,0,0)',
      },
      font: {
        family: 'Inter, sans-serif',
        size: 14,
        color: coldNight,
      },
    }

    chartConfig.value = {
      scrollZoom: false,
      displayModeBar: false,
      staticPlot: false,
      responsive: true,
    }

    if (plotlyContainer.value) {
      const plot = await Plotly.newPlot(
        plotlyContainer.value,
        chartData.value,
        chartLayout.value,
        chartConfig.value
      )

      const dragLayer = document.getElementsByClassName('nsewdrag')[0]

      plot.on('plotly_hover', function (data) {
        if (dragLayer) {
          dragLayer.style.cursor = 'pointer'
        }
        const colors = [...data.points[0].data.marker.color]
        const pointIndex = data.points[0].pointNumber
        colors[pointIndex] = coldGreenAlpha
        const update = { 'marker.color': [colors] }
        Plotly.restyle(plotlyContainer.value, update)
      })

      plot.on('plotly_unhover', function () {
        if (dragLayer) {
          dragLayer.style.cursor = 'default'
        }
        const update = { 'marker.color': [initialColors] }
        Plotly.restyle(plotlyContainer.value, update)
      })

      plot.on('plotly_click', (data) => {
        const clickedUrl = data.points[0].customdata
        if (clickedUrl) {
          window.location.href = clickedUrl
        }
      })
    } else {
      console.error('Plotly container is not ready')
    }
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false // unset loading state
  }
})
</script>

<style scoped>
.result-value-small {
  line-height: 36px !important;
}
</style>
