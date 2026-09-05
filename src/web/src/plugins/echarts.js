import ECharts from 'vue-echarts'
import { use } from 'echarts/core'

import { CanvasRenderer } from 'echarts/renderers'

import {
  LineChart,
  BarChart,
  RadarChart,
  GaugeChart
} from 'echarts/charts'

import {
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkPointComponent,
  RadarComponent
} from 'echarts/components'

import { LegacyGridContainLabel } from 'echarts/features'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  RadarChart,
  GaugeChart,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  LegacyGridContainLabel,
  DataZoomComponent,
  MarkLineComponent,
  MarkPointComponent,
  RadarComponent
])

export default {
  install(app) {
    app.component('v-chart', ECharts)
  }
}
