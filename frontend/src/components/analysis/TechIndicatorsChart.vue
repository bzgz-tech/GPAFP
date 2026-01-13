<template>
  <el-card shadow="hover" class="chart-card">
    <template #header>
      <div class="card-header">
        <span class="header-title">
          <el-icon><DataLine /></el-icon>
          技术指标详解
        </span>
         <el-radio-group :model-value="modelValue" size="small" @update:model-value="onIndicatorChange">
          <el-radio-button label="RSI" />
          <el-radio-button label="MACD" />
          <el-radio-button label="MA" />
        </el-radio-group>
      </div>
    </template>
    <div class="chart-wrapper">
        <div ref="chartRef" class="chart"></div>
    </div>
    <div class="chart-footer">
      <div class="info-block">
          <div class="info-title">
            <el-icon><InfoFilled /></el-icon> {{ info.title }}
          </div>
          <div class="info-desc">{{ info.desc }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import * as echarts from 'echarts'
import { DataLine, InfoFilled } from '@element-plus/icons-vue'
import { indicatorDefinitions } from '@/utils/analysisConstants'

const props = defineProps<{
  modelValue: string // indicator name
  data: any[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}>()

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

const info = computed(() => {
  return indicatorDefinitions[props.modelValue] || { title: '', desc: '', type: 'info' }
})

const initChart = () => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    updateChart()
  }
}

const updateChart = () => {
  if (!chart) return
  
  const unit = props.modelValue === 'RSI' ? '' : ' 元/克'
  chart.setOption({
    grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
    tooltip: { trigger: 'axis', valueFormatter: (v: number) => `${Number(v).toFixed(2)}${unit}` },
    xAxis: {
      type: 'time',
      boundaryGap: false,
      axisLabel: {
        formatter: '{MM}-{dd} {HH}:{mm}'
      }
    },
    yAxis: { type: 'value', scale: true },
    series: [{ type: 'line', data: props.data.map((d: any) => [new Date(d.ts), d.value]), smooth: true, showSymbol: false }],
  })
}

const onIndicatorChange = (val: string) => {
  emit('update:modelValue', val)
  emit('change', val)
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
