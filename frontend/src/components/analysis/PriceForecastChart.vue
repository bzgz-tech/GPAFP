<template>
  <el-card shadow="hover" class="chart-card">
    <template #header>
      <div class="card-header">
        <span class="header-title">
          <el-icon><TrendCharts /></el-icon>
          未来价格预测
        </span>
        <el-tag size="small" effect="plain">ARIMA + LSTM</el-tag>
      </div>
    </template>
    <div class="chart-wrapper">
        <div ref="chartRef" class="chart"></div>
    </div>
     <div class="chart-footer">
      <div class="info-block">
          <div class="info-title">
            <el-icon><InfoFilled /></el-icon> 预测模型说明
          </div>
          <div class="info-desc">基于 ARIMA/LSTM 混合模型，结合近期市场波动率与历史趋势进行推演。虚线区间代表 95% 置信区间。</div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { TrendCharts, InfoFilled } from '@element-plus/icons-vue'

const props = defineProps<{
  data: any[]
}>()

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

const initChart = () => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    updateChart()
  }
}

const updateChart = () => {
  if (!chart) return
  
  chart.setOption({
    grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
    tooltip: { trigger: 'axis', valueFormatter: (v: number) => `${Number(v).toFixed(2)} 元/克` },
    xAxis: { 
      type: 'time', 
      boundaryGap: false,
      axisLabel: {
         formatter: '{MM}-{dd} {HH}:{mm}'
      }
    },
    yAxis: { type: 'value', scale: true, axisLabel: { formatter: (v: number) => `${Number(v).toFixed(0)}` } },
    series: [
      { name: '预测', type: 'line', data: props.data.map((d: any) => [new Date(d.ts), d.value]), smooth: true, showSymbol: false, lineStyle: { width: 3 } },
      { name: '下界', type: 'line', data: props.data.map((d: any) => [new Date(d.ts), d.lower]), smooth: true, lineStyle: { type: 'dashed', opacity: 0.5 }, showSymbol: false },
      { name: '上界', type: 'line', data: props.data.map((d: any) => [new Date(d.ts), d.upper]), smooth: true, lineStyle: { type: 'dashed', opacity: 0.5 }, showSymbol: false },
    ],
    legend: { bottom: 0 },
  })
}

watch(() => props.data, () => {
  updateChart()
})

onMounted(() => {
  nextTick(() => {
    initChart()
  })
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
    chart = null
  }
  window.removeEventListener('resize', handleResize)
})

const handleResize = () => {
  chart && chart.resize()
}
</script>

<style scoped>
.chart-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.chart-wrapper {
  padding: 16px 0;
  background: #fff;
}

.chart {
  width: 100%;
  height: 320px;
}

.chart-footer {
  margin-top: 0;
  padding-top: 16px;
  border-top: 1px solid #f5f7fa;
}

.info-block {
  background: #f8f9fa;
  padding: 12px 16px;
  border-radius: 8px;
}

.info-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}
</style>
