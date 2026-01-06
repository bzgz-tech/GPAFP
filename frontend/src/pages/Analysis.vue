<template>
  <div class="analysis-page">
    <el-card shadow="never" class="config-card">
      <el-form :inline="true" class="config-form">
        <el-form-item label="交易品种">
          <el-select v-model="symbol" placeholder="选择品种" style="width: 120px;">
            <el-option label="XAUUSD" value="XAUUSD" />
          </el-select>
        </el-form-item>
        <el-form-item label="周期">
          <el-select v-model="timeframe" placeholder="选择周期" style="width: 100px;">
            <el-option label="日线" value="1d" />
            <el-option label="小时线" value="1h" />
            <el-option label="分钟线" value="1m" />
          </el-select>
        </el-form-item>
        <el-form-item label="显示区间">
          <el-select v-model="window" placeholder="选择区间" style="width: 120px;">
            <el-option label="最近一天" value="1d" />
            <el-option label="最近一月" value="1m" />
            <el-option label="最近三月" value="3m" />
            <el-option label="最近一年" value="1y" />
          </el-select>
        </el-form-item>
        <el-form-item label="技术指标">
          <el-select v-model="indicator" placeholder="选择指标" style="width: 100px;">
            <el-option label="RSI" value="RSI" />
            <el-option label="MACD" value="MACD" />
            <el-option label="MA" value="MA" />
          </el-select>
        </el-form-item>
        <el-form-item label="预测天数">
          <el-input-number v-model="horizon" :min="1" :max="30" :step="1" style="width: 100px;" controls-position="right" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="loadAll" :icon="Refresh">执行分析</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="summary-card" v-if="summaryItems.length > 0" style="margin-bottom: 20px;">
      <template #header>
        <div class="card-header">
          <span class="header-title">
            <el-icon><Monitor /></el-icon>
            综合信号分析
          </span>
          <el-tag type="info" effect="plain" size="small" v-if="lastUpdatedText">
            更新于: {{ lastUpdatedText }}
          </el-tag>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8" v-for="item in summaryItems" :key="item.name">
          <div class="signal-item">
            <div class="signal-header">
              <span class="signal-name">
                {{ item.name }}
                <el-tooltip :content="getIndicatorDesc(item.name)" placement="top" effect="light">
                   <el-icon class="info-icon" style="margin-left: 4px; vertical-align: middle; cursor: pointer; color: #909399;"><InfoFilled /></el-icon>
                </el-tooltip>
              </span>
              <el-tag :type="getSignalType(item.signal)" effect="dark" size="small">{{ getSignalLabel(item.signal) }}</el-tag>
            </div>
            <div class="signal-value">{{ item.value.toFixed(2) }} <span class="unit" v-if="item.unit">{{ item.unit }}</span></div>
            <div class="signal-desc">{{ item.desc }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <div class="symbol-desc" v-if="symbolInfo" style="margin-bottom: 20px;">
      <el-alert :title="symbolInfo.title" :type="symbolInfo.type" :description="symbolInfo.desc" show-icon :closable="false" />
    </div>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon><DataLine /></el-icon>
                技术指标分析 ({{ indicator }})
              </span>
            </div>
          </template>
          <div ref="indicatorRef" class="chart"></div>
          <div class="indicator-desc">
            <el-alert :title="indicatorInfo.title" :type="indicatorInfo.type" :description="indicatorInfo.desc" show-icon :closable="false" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon><TrendCharts /></el-icon>
                价格预测 (人民币元/克)
              </span>
              <el-tag v-if="predictionTrend" :type="predictionTrend.type" effect="dark" size="small" style="margin-left: 10px;">
                {{ predictionTrend.label }}
              </el-tag>
            </div>
          </template>
          <div ref="forecastRef" class="chart"></div>
          <div class="forecast-desc" v-if="predictionTrend">
            <el-alert title="预测结论" type="info" :description="predictionTrend.desc" show-icon :closable="false" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import api from '@/services/api'
import { ElMessage } from 'element-plus'
import { Refresh, DataLine, TrendCharts, Monitor, InfoFilled } from '@element-plus/icons-vue'

const symbol = ref('XAUUSD')
const timeframe = ref<'1d' | '1h' | '1m'>('1d')
const window = ref<'1d' | '1m' | '3m' | '1y'>('1m')
const indicator = ref<'RSI' | 'MACD' | 'MA'>('RSI')
const horizon = ref(1)
const loading = ref(false)
const predictionData = ref<any[]>([])
const summaryItems = ref<any[]>([])
const lastUpdated = ref<Date | null>(null)

const indicatorRef = ref<HTMLElement | null>(null)
const forecastRef = ref<HTMLElement | null>(null)
let indChart: echarts.ECharts | null = null
let fcChart: echarts.ECharts | null = null

const indicatorDefinitions: Record<string, { title: string; desc: string; type: 'success' | 'warning' | 'info' | 'error' }> = {
  RSI: {
    title: '相对强弱指标 (RSI)',
    desc: 'RSI 通过比较一段时期内的平均收盘涨数和平均收盘跌数来分析市场买卖盘的意向和实力。RSI > 70 通常表示超买（可能下跌），RSI < 30 通常表示超卖（可能上涨）。',
    type: 'warning'
  },
  MACD: {
    title: '平滑异同移动平均线 (MACD)',
    desc: 'MACD 利用收盘价的短期（常用为12日）指数移动平均线与长期（常用为26日）指数移动平均线之间的聚合与分离状况，对买进、卖出时机作出研判。',
    type: 'info'
  },
  MA: {
    title: '移动平均线 (MA)',
    desc: '移动平均线是将某一段时间的收盘价之和除以该周期，从而得到的一条带有趋势性的轨迹。它能消除价格短期波动的干扰，反映价格的长期趋势。',
    type: 'success'
  }
}

const symbolInfo = computed(() => {
  const map: Record<string, { title: string; desc: string; type: 'success' | 'warning' | 'info' | 'error' }> = {
    XAUUSD: {
      title: '现货黄金 (XAUUSD)',
      desc: 'XAUUSD 指的是现货黄金兑美元的汇率。XAU 是黄金的 ISO 4217 标准代码，USD 是美元代码。它表示 1 盎司黄金对应的美元价格。',
      type: 'info'
    }
  }
  return map[symbol.value] || { title: symbol.value, desc: '暂无描述', type: 'info' }
})

const indicatorInfo = computed(() => {
  return indicatorDefinitions[indicator.value] || { title: '', desc: '', type: 'info' }
})

const getIndicatorDesc = (name: string) => {
  return indicatorDefinitions[name]?.desc || '暂无描述'
}

const predictionTrend = computed(() => {
  if (!predictionData.value || predictionData.value.length < 2) return null
  
  // Get last historical point and last prediction point
  const lastPoint = predictionData.value[predictionData.value.length - 1]
  const prevPoint = predictionData.value[predictionData.value.length - 2]
  
  if (!lastPoint || !prevPoint) return null

  const diff = lastPoint.value - prevPoint.value
  const percent = (diff / prevPoint.value) * 100
  
  let type: 'success' | 'danger' | 'info' = 'info'
  let label = '中性'
  let desc = ''
  
  if (percent > 0.1) {
    type = 'danger' // Red for up in China
    label = '看涨'
    desc = `模型预测价格将呈现上涨趋势。预计从 ${Number(prevPoint.value).toFixed(2)} 上升至 ${Number(lastPoint.value).toFixed(2)}，涨幅约 ${percent.toFixed(2)}%。`
  } else if (percent < -0.1) {
    type = 'success' // Green for down in China
    label = '看跌'
    desc = `模型预测价格将呈现下跌趋势。预计从 ${Number(prevPoint.value).toFixed(2)} 下跌至 ${Number(lastPoint.value).toFixed(2)}，跌幅约 ${Math.abs(percent).toFixed(2)}%。`
  } else {
    type = 'info'
    label = '震荡'
    desc = `模型预测价格将保持相对平稳震荡。预计价格将在 ${Number(lastPoint.value).toFixed(2)} 附近波动，变动幅度较小。`
  }
  
  return { type, label, desc }
})

const lastUpdatedText = computed(() => {
  if (!lastUpdated.value) return ''
  return lastUpdated.value.toLocaleTimeString()
})

const getSignalType = (signal: string) => {
  if (signal === 'buy') return 'danger' // Red for buy/up
  if (signal === 'sell') return 'success' // Green for sell/down
  return 'info'
}

const getSignalLabel = (signal: string) => {
  if (signal === 'buy') return '看涨'
  if (signal === 'sell') return '看跌'
  return '中性'
}

const loadSummary = async () => {
  try {
    const { data } = await api.get('/indicator/summary', {
      params: { symbol: symbol.value, timeframe: timeframe.value },
    })
    summaryItems.value = data.items
    lastUpdated.value = new Date()
  } catch (e) {
    console.error('Error loading summary:', e)
  }
}

const initCharts = () => {
  if (indicatorRef.value) {
    if (indChart) indChart.dispose()
    indChart = echarts.init(indicatorRef.value)
  }
  if (forecastRef.value) {
    if (fcChart) fcChart.dispose()
    fcChart = echarts.init(forecastRef.value)
  }
}

const loadIndicator = async () => {
  console.log('Loading indicators...')
  try {
    const { data } = await api.get('/indicator/history', {
      params: { symbol: symbol.value, timeframe: timeframe.value, name: indicator.value, window: window.value },
    })
    console.log('Indicator data received:', data)
    
    // Ensure chart initialized
    if (!indChart && indicatorRef.value) {
      indChart = echarts.init(indicatorRef.value)
    }
    
    if (indChart) {
      const unit = indicator.value === 'RSI' ? '' : ' 元/克'
      indChart.setOption({
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
        series: [{ type: 'line', data: data.map((d: any) => [new Date(d.ts), d.value]), smooth: true, showSymbol: false }],
      })
      indChart.resize()
      console.log(`Loaded ${data.length} indicator points`)
    }
  } catch (err) {
    console.error('Error loading indicator:', err)
  }
}

const loadForecast = async () => {
  console.log('Loading forecasts...')
  try {
    const { data } = await api.get('/forecast/history', {
      params: { symbol: symbol.value, timeframe: timeframe.value, horizon: horizon.value, window: window.value },
    })
    console.log('Forecast data received:', data)
    predictionData.value = data
    
    // Ensure chart initialized
    if (!fcChart && forecastRef.value) {
      fcChart = echarts.init(forecastRef.value)
    }

    if (fcChart) {
      fcChart.setOption({
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
          { name: '预测', type: 'line', data: data.map((d: any) => [new Date(d.ts), d.value]), smooth: true, showSymbol: false, lineStyle: { width: 3 } },
          { name: '下界', type: 'line', data: data.map((d: any) => [new Date(d.ts), d.lower]), smooth: true, lineStyle: { type: 'dashed', opacity: 0.5 }, showSymbol: false },
          { name: '上界', type: 'line', data: data.map((d: any) => [new Date(d.ts), d.upper]), smooth: true, lineStyle: { type: 'dashed', opacity: 0.5 }, showSymbol: false },
        ],
        legend: { bottom: 0 },
      })
      fcChart.resize()
      console.log(`Loaded ${data.length} forecast points`)
    }
  } catch (err) {
    console.error('Error loading forecast:', err)
  }
}

const loadAll = async () => {
  loading.value = true
  try {
    await Promise.all([loadIndicator(), loadForecast(), loadSummary()])
    ElMessage.success('分析完成，数据已更新')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载失败')
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  try {
    await Promise.all([loadIndicator(), loadForecast(), loadSummary()])
  } catch (e) {
    console.error('Auto refresh failed', e)
  }
}

let timer: any = null

onMounted(() => {
  nextTick(() => {
    initCharts()
    loadAll()
  })
  globalThis.addEventListener('resize', () => {
    indChart && indChart.resize()
    fcChart && fcChart.resize()
  })
  
  // Auto refresh every 60 seconds
  timer = setInterval(refreshData, 60000)
})

onUnmounted(() => {
  if (indChart) {
    indChart.dispose()
    indChart = null
  }
  if (fcChart) {
    fcChart.dispose()
    fcChart = null
  }
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})
</script>

<style scoped>
.analysis-page {
  /* No padding needed */
  overflow-x: hidden;
}
.config-card {
  margin-bottom: 20px;
  border: none;
}
.config-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
:deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 24px;
}
.charts-row {
  margin-bottom: 20px;
}
.chart-card {
  border: none;
}
.card-header {
  display: flex;
  align-items: center;
}
.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
.chart {
  height: 400px;
}
.indicator-desc, .forecast-desc {
  padding: 10px 20px;
}
.summary-card :deep(.el-card__body) {
  overflow: hidden;
}
.signal-item {
  text-align: center;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
  height: 100%;
}
.signal-header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.signal-name {
  font-weight: bold;
  font-size: 16px;
  display: flex;
  align-items: center;
}
.signal-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}
.unit {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
  margin-left: 4px;
}
.signal-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
}
</style>
