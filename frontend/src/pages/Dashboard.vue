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
            <span>K线走势</span>
          </div>
          <div class="chart-controls">
            <el-checkbox-group v-model="selectedIndicators" size="small" @change="loadChart">
              <el-checkbox-button label="MA">MA</el-checkbox-button>
              <el-checkbox-button label="MACD">MACD</el-checkbox-button>
              <el-checkbox-button label="RSI">RSI</el-checkbox-button>
              <el-checkbox-button label="KDJ">KDJ</el-checkbox-button>
              <el-checkbox-button label="SUPPORT">支撑</el-checkbox-button>
              <el-checkbox-button label="RESISTANCE">压力</el-checkbox-button>
            </el-checkbox-group>
            <el-radio-group v-model="range" size="small" @change="loadChart">
              <el-radio-button label="1m">1分</el-radio-button>
              <el-radio-button label="5m">5分</el-radio-button>
              <el-radio-button label="15m">15分</el-radio-button>
              <el-radio-button label="1h">1时</el-radio-button>
              <el-radio-button label="1d">日K</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>
      <div ref="chartRef" class="chart"></div>
    </el-card>

    <el-row :gutter="20" class="bottom-row">
      <el-col :span="14">
        <el-card shadow="never" class="bottom-card">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon><Reading /></el-icon>
                <span>市场资讯</span>
              </div>
              <el-tag size="small" type="info">实时聚合</el-tag>
            </div>
          </template>
          <el-table :data="newsList" style="width: 100%; height: 100%" stripe :show-header="false">
            <el-table-column width="80">
               <template #default="{ row }">
                  <el-tag size="small" :type="getImpactType(row.impact)">{{ getImpactLabel(row.impact) }}</el-tag>
               </template>
            </el-table-column>
            <el-table-column prop="title" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="news-title">{{ row.title }}</span>
                <span class="news-time">{{ formatTime(row.published_at) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="category" width="80" align="right">
               <template #default="{ row }">
                 <el-tag size="small" effect="plain">{{ getCategoryLabel(row.category) }}</el-tag>
               </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="10">
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
import { Money, TrendCharts, Aim, Bell, Histogram, Timer, Plus, Delete, Reading } from '@element-plus/icons-vue'

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null
const range = ref<'1m' | '5m' | '15m' | '1h' | '1d'>('1d')
const selectedIndicators = ref<string[]>(['MA'])
const latestDisplay = ref('—')
const latestTime = ref('')
const nextDayForecast = ref('—')
const forecastTime = ref('')
const dailyChange = ref('—')
const dailyChangeTime = ref('')
const status = ref<any>({})
const alerts = ref<any[]>([])
const newsList = ref<any[]>([])
const dialogVisible = ref(false)
const creating = ref(false)
const alertForm = reactive({
  name: '',
  symbol: 'XAUUSD',
  condition: 'price_above',
  threshold: 0
})

const getImpactType = (impact: string) => {
  if (impact === 'Bullish') return 'danger'
  if (impact === 'Bearish') return 'success' // Green for bearish in China? Or usually Red=Up/Green=Down.
  // In China: Red=Up (Bullish), Green=Down (Bearish).
  // "利多" -> Bullish -> Red -> danger. "利空" -> Bearish -> Green -> success.
  return 'info'
}

const getImpactLabel = (impact: string) => {
  if (impact === 'Bullish') return '利多'
  if (impact === 'Bearish') return '利空'
  return '中性'
}

const getCategoryLabel = (cat: string) => {
  const map: Record<string, string> = {
    'Policy': '政策',
    'Data': '数据',
    'Geopolitics': '地缘'
  }
  return map[cat] || cat
}

const taskList = computed(() => {
  // ... (Keep existing if needed, but we removed the table from UI. Can delete this block or keep for debug)
  return [] 
})
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
    const timeframe = range.value
    let windowStr = '1d'
    
    if (timeframe === '1m' || timeframe === '5m' || timeframe === '15m' || timeframe === '1h') {
        windowStr = '5d' 
        if (timeframe === '1m') windowStr = '1d' 
    } else if (timeframe === '1d') {
        windowStr = '1y'
    }

    // Fetch Price Data
    const { data: priceData } = await api.get('/market/history/detailed', {
      params: { symbol: 'XAUUSD', timeframe, window: windowStr },
    })
    
    // Sort by TS ascending
    priceData.sort((a: any, b: any) => new Date(a.ts).getTime() - new Date(b.ts).getTime())
    
    const dates = priceData.map((d: any) => d.ts)
    // ECharts Candle: [Open, Close, Lowest, Highest]
    const values = priceData.map((d: any) => [d.open, d.close, d.low, d.high])
    
    // Fetch Indicators
    const indicatorsData: any = {}
    
    // Expand composite indicators
    const requests = []
    for (const ind of selectedIndicators.value) {
        if (ind === 'KDJ') {
            requests.push('KDJ_K', 'KDJ_D', 'KDJ_J')
        } else {
            requests.push(ind)
        }
    }

    for (const req of requests) {
        try {
            const { data } = await api.get('/indicator/history', {
                params: { symbol: 'XAUUSD', timeframe, name: req }
            })
            const map = new Map()
            data.forEach((d: any) => map.set(new Date(d.ts).getTime(), d.value))
            
            // Align with price dates
            const series = dates.map((d: string) => map.get(new Date(d).getTime()) || null)
            indicatorsData[req] = series
        } catch (e) {
            console.error(`Failed to load ${req}`, e)
        }
    }

    if (!chart && chartRef.value) initChart()
    
    if (chart) {
        const option: any = {
             tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'cross' }
             },
             grid: [
                 { left: '3%', right: '3%', top: '10%', height: '55%' },
                 { left: '3%', right: '3%', top: '75%', height: '20%' }
             ],
             xAxis: [
                 { type: 'category', data: dates.map((d: string) => new Date(d).toLocaleString()), scale: true, boundaryGap: false, gridIndex: 0, axisLabel: { show: false } },
                 { type: 'category', data: dates.map((d: string) => new Date(d).toLocaleString()), scale: true, boundaryGap: false, gridIndex: 1 }
             ],
             yAxis: [
                 { scale: true, gridIndex: 0, splitLine: { show: false } },
                 { scale: true, gridIndex: 1, splitLine: { show: false } }
             ],
             dataZoom: [{ type: 'inside', xAxisIndex: [0, 1] }, { type: 'slider', xAxisIndex: [0, 1] }],
             series: [
                 {
                     type: 'candlestick',
                     name: 'Gold',
                     data: values,
                     itemStyle: {
                         color: '#ef232a',
                         color0: '#14b143',
                         borderColor: '#ef232a',
                         borderColor0: '#14b143'
                     }
                 }
             ]
        }
        
        // Add Indicators
        // MA -> Main Chart
        if (indicatorsData['MA']) {
            option.series.push({
                name: 'MA20',
                type: 'line',
                data: indicatorsData['MA'],
                smooth: true,
                symbol: 'none',
                lineStyle: { opacity: 0.8, width: 1 }
            })
        }
        
        // Sub Chart Logic
        let hasSubChart = false
        
        if (indicatorsData['RSI']) {
             option.series.push({
                name: 'RSI',
                type: 'line',
                xAxisIndex: 1,
                yAxisIndex: 1,
                data: indicatorsData['RSI'],
                symbol: 'none',
                itemStyle: { color: '#fa8c16' }
             })
             hasSubChart = true
        }
        
        if (indicatorsData['MACD']) {
             // MACD usually has DIFF, DEA, HIST. My backend returns DIFF by default for "MACD".
             // Assuming user wants simple line for now or I should have fetched 3 parts.
             // Let's just show DIFF line.
             option.series.push({
                name: 'MACD',
                type: 'line',
                xAxisIndex: 1,
                yAxisIndex: 1,
                data: indicatorsData['MACD'],
                symbol: 'none',
                itemStyle: { color: '#1890ff' }
             })
             hasSubChart = true
        }

        if (indicatorsData['KDJ_K']) {
              option.series.push(
                 { name: 'K', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: indicatorsData['KDJ_K'], symbol: 'none', itemStyle: { color: '#eb2f96' } },
                 { name: 'D', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: indicatorsData['KDJ_D'], symbol: 'none', itemStyle: { color: '#faad14' } },
                 { name: 'J', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: indicatorsData['KDJ_J'], symbol: 'none', itemStyle: { color: '#722ed1' } }
              )
              hasSubChart = true
         }
         
         if (indicatorsData['SUPPORT']) {
              option.series.push({
                  name: 'Support',
                  type: 'line',
                  data: indicatorsData['SUPPORT'],
                  smooth: true,
                  symbol: 'none',
                  lineStyle: { type: 'dashed', color: '#14b143', width: 1.5 }
              })
         }

         if (indicatorsData['RESISTANCE']) {
              option.series.push({
                  name: 'Resistance',
                  type: 'line',
                  data: indicatorsData['RESISTANCE'],
                  smooth: true,
                  symbol: 'none',
                  lineStyle: { type: 'dashed', color: '#ef232a', width: 1.5 }
              })
         }
        
         if (!hasSubChart) {
            // Hide bottom grid if no subchart indicators
            option.grid[0].height = '80%'
            option.grid[1].height = '0%'
            option.xAxis[0].axisLabel = { show: true }
            option.xAxis[1].show = false
            option.yAxis[1].show = false
        }
        
        chart.setOption(option, true)
    }
  } catch (e: any) {
    console.error('Load chart error:', e)
    ElMessage.error(e?.response?.data?.detail || '加载图表数据失败')
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

const loadNews = async () => {
  try {
    const { data } = await api.get('/news/')
    newsList.value = data
  } catch (e) {
    console.error('Load news error', e)
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
  loadNews()
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
    loadNews()
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
.chart-controls {
  display: flex;
  gap: 16px;
  align-items: center;
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
.news-title {
  font-weight: 500;
  color: #333;
}
.news-time {
  margin-left: 8px;
  color: #999;
  font-size: 12px;
}
</style>
