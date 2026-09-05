import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'
import echartsPlugin from './plugins/echarts'

const app = createApp(App)

// Instala o plugin do Vue-ECharts
app.use(echartsPlugin)

app.mount('#app')
