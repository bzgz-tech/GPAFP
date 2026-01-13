<template>
  <div class="analysis-page">
    <div class="page-header">
      <div class="header-content">
        <div class="title-group">
          <div class="icon-wrapper">
            <el-icon :size="32" color="#409eff"><DataLine /></el-icon>
          </div>
          <div>
            <h1 class="page-title">AI 市场智能分析报告</h1>
            <p class="page-subtitle">基于多维技术指标与机器学习模型的深度市场预测</p>
          </div>
        </div>
      </div>
    </div>

    <div class="section-container">
      <el-row :gutter="20">
        <el-col :span="24">
          <ConfigPanel
            v-model:symbol="symbol"
            v-model:timeframe="timeframe"
            v-model:timeWindow="timeWindow"
            v-model:horizon="horizon"
            :loading="loading"
            @analyze="loadAll"
          />
        </el-col>
      </el-row>
    </div>

    <div class="section-container" v-if="predictionTrend">
      <el-row :gutter="20">
        <el-col :span="24">
          <TrendStrategy
            :prediction-trend="predictionTrend"
            :horizon="horizon"
          />
        </el-col>
      </el-row>
    </div>

    <div class="section-container" v-if="summaryItems.length > 0">
      <el-row :gutter="20">
        <el-col :span="24">
          <SignalDashboard
            :items="summaryItems"
            :last-updated-text="lastUpdatedText"
          />
        </el-col>
      </el-row>
    </div>

    <div class="section-container" v-if="aiReport">
      <el-row :gutter="20">
        <el-col :span="24">
          <AiReport
            :report="aiReport"
            :model="aiModel"
          />
        </el-col>
      </el-row>
    </div>

    <div class="section-container charts-section">
      <el-row :gutter="20">
        <el-col :span="12">
          <TechIndicatorsChart
            v-model="indicator"
            :data="indicatorData"
            @change="loadIndicator"
          />
        </el-col>
        <el-col :span="12">
          <PriceForecastChart
            :data="predictionData"
          />
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataLine } from '@element-plus/icons-vue'

import ConfigPanel from '@/components/analysis/ConfigPanel.vue'
import SignalDashboard from '@/components/analysis/SignalDashboard.vue'
import AiReport from '@/components/analysis/AiReport.vue'
import TrendStrategy from '@/components/analysis/TrendStrategy.vue'
import TechIndicatorsChart from '@/components/analysis/TechIndicatorsChart.vue'
import PriceForecastChart from '@/components/analysis/PriceForecastChart.vue'

const router = useRouter()
const symbol = ref('XAUUSD')
const timeframe = ref<'1d' | '1h' | '1m'>('1d')
const timeWindow = ref<'1d' | '7d' | '1m' | '3m' | '1y'>('1m')
const indicator = ref('RSI')
const horizon = ref(1)

const loading = ref(false)
const indicatorData = ref<any[]>([])
const predictionData = ref<any[]>([])
const summaryItems = ref<any[]>([])
const aiReport = ref('')
const aiModel = ref('')
const lastUpdated = ref<Date | null>(null)

const lastUpdatedText = computed(() => {
  if (!lastUpdated.value) return ''
  return lastUpdated.value.toLocaleTimeString()
})

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
    desc = `模型预测未来 ${horizon.value} 天内价格将呈现上涨趋势。预计从 ${Number(prevPoint.value).toFixed(2)} 上升至 ${Number(lastPoint.value).toFixed(2)}，涨幅约 ${percent.toFixed(2)}%。建议关注多头机会。`
  } else if (percent < -0.1) {
    type = 'success' // Green for down in China
    label = '看跌'
    desc = `模型预测未来 ${horizon.value} 天内价格将呈现下跌趋势。预计从 ${Number(prevPoint.value).toFixed(2)} 下跌至 ${Number(lastPoint.value).toFixed(2)}，跌幅约 ${Math.abs(percent).toFixed(2)}%。建议关注空头风险。`
  } else {
    type = 'info'
    label = '震荡'
    desc = `模型预测未来 ${horizon.value} 天内价格将保持相对平稳震荡。预计价格将在 ${Number(lastPoint.value).toFixed(2)} 附近波动，变动幅度较小。建议观望或进行区间操作。`
  }
  
  return { type, label, desc }
})

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

const loadIndicator = async () => {
  console.log('Loading indicators...')
  try {
    const { data } = await api.get('/indicator/history', {
      params: { symbol: symbol.value, timeframe: timeframe.value, name: indicator.value, window: timeWindow.value },
    })
    console.log('Indicator data received:', data)
    indicatorData.value = data
  } catch (err) {
    console.error('Error loading indicator:', err)
  }
}

const loadForecast = async () => {
  console.log('Loading forecasts...')
  try {
    const { data } = await api.get('/forecast/history', {
      params: { symbol: symbol.value, timeframe: timeframe.value, horizon: horizon.value, window: timeWindow.value },
    })
    console.log('Forecast data received:', data)
    predictionData.value = data
  } catch (err) {
    console.error('Error loading forecast:', err)
  }
}

const loadAiReport = async () => {
  // Check AI config first
  try {
    const { data: status } = await api.get('/settings/config/ai_status')
    if (status.model) {
      aiModel.value = status.model
    }

    if (!status.configured) {
      ElMessageBox.confirm(
        'AI 大模型信息缺失，无法生成深度分析报告。是否前往系统设置进行配置？',
        '配置缺失',
        {
          confirmButtonText: '去配置',
          cancelButtonText: '暂不配置',
          type: 'warning',
        }
      )
        .then(() => {
          router.push('/settings')
        })
        .catch(() => {
          ElMessage.info('已取消生成 AI 报告')
        })
      return
    }

    console.log('Loading AI report...', { symbol: symbol.value, timeframe: timeframe.value, window: timeWindow.value })
    const { data } = await api.get('/analysis/ai_report', {
      params: { symbol: symbol.value, timeframe: timeframe.value, window: timeWindow.value },
    })
    aiReport.value = data.report
    if (data.model) {
      aiModel.value = data.model
    }
  } catch (e) {
    console.error('Error loading AI report:', e)
  }
}

const loadAll = async () => {
  loading.value = true
  try {
    // Parallel load charts and summary first
    await Promise.all([loadIndicator(), loadForecast(), loadSummary()])
    
    // Then try to load AI report (separate try-catch to not block others if config missing)
    await loadAiReport()
    
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
    loadAll()
  })
  
  // Auto refresh every 60 seconds
  timer = setInterval(refreshData, 60000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})
</script>

<style scoped>
.analysis-page {
  padding: 24px;
  padding-bottom: 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-wrapper {
  width: 56px;
  height: 56px;
  background: #ecf5ff;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
  font-weight: 400;
}

.section-container {
  margin-bottom: 32px;
}
</style>
