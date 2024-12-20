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
          @on-ready="myChartOnReady"
        ></nuxt-plotly>
      </client-only>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import {
  NuxtPlotlyConfig,
  NuxtPlotlyData,
  NuxtPlotlyLayout,
  NuxtPlotlyHTMLElement,
} from 'nuxt-plotly'

const x = [1, 2, 3, 4, 5]
const y = [10, 20, 30, 20, 10]
const data: NuxtPlotlyData = [
  { x: x, y: y, type: 'scatter', mode: 'markers', marker: { size: 20 } },
]
const layout: NuxtPlotlyLayout = {
  title: 'My graph on app.vue with <client-only>',
}

const config: NuxtPlotlyConfig = { scrollZoom: true, displayModeBar: false }

function myChartOnReady(plotlyHTMLElement: NuxtPlotlyHTMLElement) {
  const { $plotly } = useNuxtApp()
  console.log({ $plotly })
  console.log({ plotlyHTMLElement })

  plotlyHTMLElement.on?.('plotly_afterplot', function () {
    console.log('done plotting')
  })

  plotlyHTMLElement.on?.('plotly_click', function () {
    alert('You clicked this Plotly chart!')

    // use plotly function via `$plotly` to download chart image
    $plotly.downloadImage(plotlyHTMLElement as HTMLElement, {
      format: 'png',
      width: 800,
      height: 600,
      filename: 'newplot',
    })
  })
}
</script>
