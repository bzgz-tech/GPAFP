<template>
  <div class="dashboard">
    <el-row :gutter="20" class="top-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon-wrapper money">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-title">实时金价</div>
            <div class="stat-value">{{ latestDisplay }} <span class="unit">元/克</span></div>
            <div class="stat-time" v-if="latestTime">{{ latestTime }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon-wrapper trend">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-title">日涨跌</div>
            <div class="stat-value" :class="getChangeClass(dailyChange)">{{ dailyChange }}</div>
            <div class="stat-time" v-if="dailyChangeTime">{{ dailyChangeTime }}</div>
            <div class="stat-desc">
              <span class="text-up">红涨(+)</span> / <span class="text-down">绿跌(-)</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon-wrapper forecast">
            <el-icon><Aim /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-title">次日预测</div>
            <div class="stat-value">{{ nextDayForecast }} <span class="unit">元/克</span></div>
            <div class="stat-time" v-if="forecastTime">{{ forecastTime }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon-wrapper warning">
            <el-icon><Bell /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-title">活跃告警</div>
            <div class="stat-value">{{ alerts.length }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="chart-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><Histogram /></el-icon>
            <span>历史价格走势</span>
          </div>
          <el-radio-group v-model="range" size="small" @change="loadChart">
            <el-radio-button label="1d">1天</el-radio-button>
            <el-radio-button label="1m">1月</el-radio-button>
            <el-radio-button label="3m">3月</el-radio-button>
            <el-radio-button label="1y">1年</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="chartRef" class="chart"></div>
    </el-card>

    <el-row :gutter="20" class="bottom-row">
      <el-col :span="12">
        <el-card shadow="never" class="bottom-card">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon><Timer /></el-icon>
                <span>数据采集状态</span>
              </div>
              <el-button link type="primary" @click="loadStatus">刷新</el-button>
            </div>
          </template>
          <el-table :data="taskList" style="width: 100%; height: 100%" stripe>
            <el-table-column prop="name" label="任务名称" />
            <el-table-column prop="lastRun" label="上次执行" width="160" />
            <el-table-column prop="inserted" label="采集数量" width="100" />
            <el-table-column prop="totalRuns" label="总执行次数" width="100" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag v-if="!row.error" type="success" size="small">正常</el-tag>
                <el-tooltip v-else :content="row.error" placement="top">
                  <el-tag type="danger" size="small">异常</el-tag>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="never" class="bottom-card">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon><Bell /></el-icon>
                <span>活跃告警</span>
              </div>
              <el-button type="primary" link @click="openAlertDialog">
                <el-icon><Plus /></el-icon> 新增
              </el-button>
            </div>
          </template>
          <el-table :data="alerts" style="width: 100%; height: 100%" stripe empty-text="暂无活跃告警">
            <el-table-column prop="name" label="名称" />
            <el-table-column label="条件" width="120">
              <template #default="{ row }">
                {{ row.condition === 'price_above' ? '高于' : '低于' }} {{ row.threshold }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center">
              <template #default="{ row }">
                <el-button type="danger" link size="small" @click="deleteAlert(row.id)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Add Alert Dialog -->
    <el-dialog v-model="dialogVisible" title="新增告警" width="400px">
      <el-form :model="alertForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="alertForm.name" placeholder="例如：突破800" />
        </el-form-item>
        <el-form-item label="条件">
          <el-select v-model="alertForm.condition" placeholder="选择条件">
            <el-option label="价格高于" value="price_above" />
            <el-option label="价格低于" value="price_below" />
          </el-select>
        </el-form-item>
        <el-form-item label="阈值">
          <el-input-number v-model="alertForm.threshold" :precision="2" :step="1" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createAlert" :loading="creating">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '@/services/api'
import { ElMessage } from 'element-plus'
import { Money, TrendCharts, Aim, Bell, Histogram, Timer, Plus, Delete } from '@element-plus/icons-vue'

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null
const range = ref<'1d' | '1m' | '3m' | '1y'>('1d')
const latestDisplay = ref('—')
const latestTime = ref('')
const nextDayForecast = ref('—')
const forecastTime = ref('')
const dailyChange = ref('—')
const dailyChangeTime = ref('')
const status = ref<any>({})
const alerts = ref<any[]>([])
const dialogVisible = ref(false)
const creating = ref(false)
const alertForm = reactive({
  name: '',
  symbol: 'XAUUSD',
  condition: 'price_above',
  threshold: 0
})

const taskList = computed(() => {
  const list = []
  if (status.value.realtime_data_fetch) {
    list.push({
      name: '实时监控 (1m)',
      type: 'success',
      lastRun: formatTime(status.value.realtime_data_fetch.last_run),
      inserted: status.value.realtime_data_fetch.inserted ?? 0,
      totalRuns: status.value.realtime_data_fetch.total_runs ?? 0,
      error: status.value.realtime_data_fetch.error
    })
  }
  if (status.value.hourly_data_fetch) {
    list.push({
      name: '小时线采集',
      type: 'primary',
      lastRun: formatTime(status.value.hourly_data_fetch.last_run),
      inserted: status.value.hourly_data_fetch.inserted ?? 0,
      totalRuns: status.value.hourly_data_fetch.total_runs ?? 0,
      error: status.value.hourly_data_fetch.error
    })
  }
  if (status.value.daily_data_fetch) {
    list.push({
      name: '日线采集',
      type: 'warning',
      lastRun: formatTime(status.value.daily_data_fetch.last_run),
      inserted: status.value.daily_data_fetch.inserted ?? 0,
      totalRuns: status.value.daily_data_fetch.total_runs ?? 0,
      error: status.value.daily_data_fetch.error
    })
  }
  return list
})

const getChangeClass = (val: string) => {
  if (val.includes('+')) return 'text-up'
  if (val.includes('-')) return 'text-down'
  return ''
}

const initChart = () => {
  if (chartRef.value) {
    // Dispose existing chart if any
    if (chart) {
      chart.dispose()
    }
    console.log('Initializing chart. Container size:', chartRef.value.clientWidth, chartRef.value.clientHeight)
    chart = echarts.init(chartRef.value)
  }
}

const loadRealtimeStats = async () => {
  try {
    // 1. Get latest real-time price (1m)
    const { data: latestData } = await api.get('/market/latest', {
      params: { symbol: 'XAUUSD', timeframe: '1m' }
    })
    
    let currentPrice = 0
    let currentTime = null
    
    if (latestData) {
      currentPrice = latestData.close
      latestDisplay.value = Number(currentPrice).toFixed(2)
      
      if (latestData.ts) {
        currentTime = new Date(latestData.ts)
        const month = (currentTime.getMonth() + 1).toString().padStart(2, '0')
        const day = currentTime.getDate().toString().padStart(2, '0')
        const hours = currentTime.getHours().toString().padStart(2, '0')
        const minutes = currentTime.getMinutes().toString().padStart(2, '0')
        const seconds = currentTime.getSeconds().toString().padStart(2, '0')
        latestTime.value = `${month}-${day} ${hours}:${minutes}:${seconds}`
        dailyChangeTime.value = latestTime.value
      }
      
      // Set default threshold for alert
      if (alertForm.threshold === 0) {
        alertForm.threshold = Math.round(currentPrice)
      }
    }

    // 2. Get daily history to calculate change from yesterday's close
    const { data: historyData } = await api.get('/market/history', {
      params: { symbol: 'XAUUSD', timeframe: '1d', window: '1m' } // Get 1 month of daily data
    })
    
    if (historyData && historyData.length > 0 && currentPrice > 0) {
      // Find the previous day's close
      // historyData is sorted by ts ascending
      // We need to find the last record that is NOT today (strictly less than today's date)
      // OR simply:
      // If the last record is today, take the one before it.
      // If the last record is yesterday, take it.
      
      // Let's rely on dates.
      const today = new Date()
      // Reset time to 00:00:00 for comparison
      const todayStr = today.toISOString().split('T')[0]
      
      // Check last point
      const lastPoint = historyData[historyData.length - 1]
      const lastPointDate = new Date(lastPoint.ts).toISOString().split('T')[0]
      
      let prevClose = 0
      
      if (lastPointDate === todayStr) {
        // Last point is today, so prev close is the one before
        if (historyData.length >= 2) {
          prevClose = historyData[historyData.length - 2].value
        }
      } else {
        // Last point is not today (likely yesterday), so it IS the prev close
        prevClose = lastPoint.value
      }
      
      if (prevClose > 0) {
        const diff = currentPrice - prevClose
        const pct = (diff / prevClose) * 100
        dailyChange.value = `${diff >= 0 ? '+' : ''}${pct.toFixed(2)}%`
      }
    }
    
  } catch (e) {
    console.error('Load realtime stats error:', e)
  }
}

const loadChart = async () => {
  try {
    // Use 1m (minute) data for 1d range to show real-time trend
    // Use 1d (daily) data for other ranges (1m, 3m, 1y) for macro trend
    // For 1m range, we could use 1h data, but let's keep it simple for now
    let timeframe = '1d'
    if (range.value === '1d') {
      timeframe = '1m'
    } else if (range.value === '1m') {
      timeframe = '1h'
    }

    const { data } = await api.get('/market/history', {
      params: { symbol: 'XAUUSD', timeframe, window: range.value },
    })
    
    // Ensure chart is initialized
    if (!chart && chartRef.value) {
      initChart()
    }

    if (chart) {
      const seriesData = data.map((d: any) => [new Date(d.ts), d.value])
      
      const option = {
        grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
        tooltip: { 
          trigger: 'axis', 
          valueFormatter: (v: number) => `¥${Number(v).toFixed(2)}` 
        },
        xAxis: { 
          type: 'time', 
          boundaryGap: false,
          axisLabel: {
             formatter: '{MM}-{dd} {HH}:{mm}'
          }
        },
        yAxis: { 
          type: 'value', 
          scale: true, 
          axisLabel: { formatter: (v: number) => `¥${v.toFixed(0)}` } 
        },
        series: [{
          type: 'line',
          data: seriesData,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 3, color: '#1890ff' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(24,144,255,0.3)' },
              { offset: 1, color: 'rgba(24,144,255,0.01)' }
            ])
          }
        }],
      }
      
      console.log('Setting chart option:', option)
      chart.setOption(option)
      chart.resize()
    }
    
    
    // Stats are now handled by loadRealtimeStats independently
  } catch (e: any) {
    console.error('Load chart error:', e)
    ElMessage.error(e?.response?.data?.detail || '加载历史数据失败')
  }
}

const loadStatus = async () => {
  try {
    const { data } = await api.get('/tasks/status')
    status.value = data
  } catch {
    status.value = {}
  }
}

const loadForecast = async () => {
  try {
    const { data } = await api.get('/forecast/latest', {
      params: { symbol: 'XAUUSD', timeframe: '1d', horizon: 1 }
    })
    if (data && data.value) {
      nextDayForecast.value = Number(data.value).toFixed(2)
      if (data.ts) {
        const date = new Date(data.ts)
        const month = (date.getMonth() + 1).toString().padStart(2, '0')
        const day = date.getDate().toString().padStart(2, '0')
        const hours = date.getHours().toString().padStart(2, '0')
        const minutes = date.getMinutes().toString().padStart(2, '0')
        forecastTime.value = `${month}-${day} ${hours}:${minutes}`
      }
    }
  } catch (e) {
    console.error('Load forecast error:', e)
    nextDayForecast.value = '—'
    forecastTime.value = ''
  }
}

const loadAlerts = async () => {
  try {
    const { data } = await api.get('/alert/active')
    alerts.value = data
  } catch {
    alerts.value = []
  }
}

const openAlertDialog = () => {
  dialogVisible.value = true
}

const createAlert = async () => {
  creating.value = true
  try {
    await api.post('/alert/', alertForm)
    ElMessage.success('告警添加成功')
    dialogVisible.value = false
    loadAlerts()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '添加失败')
  } finally {
    creating.value = false
  }
}

const deleteAlert = async (id: number) => {
  try {
    await api.delete(`/alert/${id}`)
    ElMessage.success('已删除')
    loadAlerts()
  } catch (e: any) {
    ElMessage.error('删除失败')
  }
}

const formatTime = (t: string | null | undefined) => {
  if (!t) return '—'
  return new Date(t).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
}

let timer: any = null

onMounted(() => {
  nextTick(() => {
    initChart()
    loadChart()
  })
  loadRealtimeStats()
  loadStatus()
  loadAlerts()
  loadForecast()
  globalThis.addEventListener('resize', () => chart && chart.resize())
  
  // Refresh data every 10 seconds to show real-time updates
  timer = setInterval(() => {
    // Note: We do NOT refresh chart automatically here to avoid resetting user's zoom/view if they are interacting
    // But for now, we keep it simple. If we want "Real-time Chart", we should only update if range is '1d'.
    // However, user asked for stats to be independent.
    // Let's keep updating chart for now, but stats update is separate.
    if (range.value === '1d') {
        loadChart()
    }
    loadRealtimeStats()
    loadForecast()
    loadStatus()
    loadAlerts()
  }, 10000)
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
    chart = null
  }
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})
</script>

<style scoped>
.dashboard {
  height: calc(100vh - 112px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.stat-card {
  display: flex;
  align-items: center;
  border: none;
  height: 100%;
}
.top-row {
  flex-shrink: 0;
  margin-bottom: 20px;
}
.bottom-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.bottom-card :deep(.el-card__body) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 0;
}
:deep(.el-card__body) {
  display: flex;
  align-items: center;
  padding: 20px !important;
  width: 100%;
  overflow: hidden;
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
}
.stat-icon-wrapper.money { background: #e6f7ff; color: #1890ff; }
.stat-icon-wrapper.trend { background: #f6ffed; color: #52c41a; }
.stat-icon-wrapper.forecast { background: #fff7e6; color: #fa8c16; }
.stat-icon-wrapper.warning { background: #fff1f0; color: #f5222d; }

.stat-content {
  flex: 1;
}
.stat-title {
  font-size: 14px;
  color: #8c8c8c;
  margin-bottom: 4px;
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #262626;
  font-family: 'DIN Alternate', 'Helvetica Neue', sans-serif;
}
.stat-time {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}
.stat-desc {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 2px;
}
.text-up { color: #f5222d; }
.text-down { color: #52c41a; }
.text-success { color: #52c41a; }
.text-danger { color: #f5222d; }

.unit {
  font-size: 14px;
  color: #8c8c8c;
  font-weight: normal;
  margin-left: 4px;
}

.chart-card {
  flex: 3;
  min-height: 0;
  display: flex;
  flex-direction: column;
  margin-bottom: 10px;
  border: none;
}
.chart-card :deep(.el-card__body) {
  flex: 1;
  min-height: 0;
  padding: 10px;
  display: block;
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
}
.chart {
  width: 100%;
  height: 100%;
}
.bottom-row {
  flex: 2;
  min-height: 0;
  margin-top: 0;
}
</style>
