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

    <!-- Historical Price Chart (Restored V1.0.0 Feature) -->
    <el-card class="chart-card" shadow="never" style="margin-bottom: 20px;">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><TrendCharts /></el-icon>
            <span>历史价格走势图</span>
          </div>
          <el-radio-group v-model="historyRange" size="small" @change="loadHistoryChart">
            <el-radio-button label="1d">今日</el-radio-button>
            <el-radio-button label="1m">1月</el-radio-button>
            <el-radio-button label="3m">3月</el-radio-button>
            <el-radio-button label="6m">6月</el-radio-button>
            <el-radio-button label="1y">1年</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="historyChartRef" class="chart" style="height: 400px;"></div>
    </el-card>

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
            <el-button link size="small" @click="openSettingsDialog" style="margin-left: 10px">
                <el-icon><Setting /></el-icon>
            </el-button>
          </div>
        </div>
      </template>
      <div style="display: flex; height: 500px;">
          <div ref="chartRef" class="chart" style="flex: 1; height: 100%;"></div>
          <div class="chart-info-panel">
              <div class="info-title">
                  <el-icon><InfoFilled /></el-icon> 实时指标解读
              </div>
              <div class="info-list" v-if="latestIndicators.length > 0">
                  <div v-for="item in latestIndicators" :key="item.name" class="info-item">
                      <div class="info-header">
                          <span class="info-label" :style="{ color: item.color }">{{ item.label }}</span>
                          <span class="info-value">{{ item.value }}</span>
                      </div>
                      <div class="info-desc">{{ item.desc }}</div>
                  </div>
              </div>
              <div v-else class="info-empty">
                  <p>暂无指标数据</p>
                  <p style="font-size: 12px; color: #999;">请在上方勾选指标以查看详细解读</p>
              </div>
          </div>
      </div>
    </el-card>

    <el-row :gutter="20" class="bottom-row" style="margin-bottom: 20px;">
      <el-col :span="12">
        <el-card shadow="never" class="bottom-card" :body-style="{ padding: '10px' }">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon><Bell /></el-icon>
                <span>活跃告警</span>
              </div>
              <el-button type="primary" link @click="openAlertDialog" size="small">
                <el-icon><Plus /></el-icon> 新增
              </el-button>
            </div>
          </template>
          <el-table :data="alerts" style="width: 100%; height: 100%" stripe empty-text="暂无活跃告警" size="small">
            <el-table-column prop="name" label="名称" show-overflow-tooltip />
            <el-table-column label="条件" width="100">
              <template #default="{ row }">
                <span :class="row.condition === 'price_above' ? 'text-up' : 'text-down'">
                    {{ row.condition === 'price_above' ? '≥' : '≤' }} {{ row.threshold }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="60" align="center">
              <template #default="{ row }">
                <el-button type="danger" link size="small" @click="deleteAlert(row.id)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="bottom-card" :body-style="{ padding: '10px' }">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon><Timer /></el-icon>
                <span>采集状态</span>
              </div>
              <el-tag size="small" type="success">正常运行</el-tag>
            </div>
          </template>
          <el-table :data="taskList" style="width: 100%; height: 100%" stripe size="small">
            <el-table-column prop="name" label="任务" show-overflow-tooltip />
            <el-table-column label="上次运行" width="140">
              <template #default="{ row }">
                <span :class="row.error ? 'text-danger' : ''" style="font-size: 12px;">{{ row.lastRun }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="inserted" label="新增" width="50" align="center" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="news-row">
      <el-col :span="24">
        <el-card shadow="never" class="bottom-card" :body-style="{ padding: '10px' }">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon><Reading /></el-icon>
                <span>市场资讯</span>
              </div>
              <el-tag size="small" type="info">实时聚合</el-tag>
            </div>
          </template>
          <el-table :data="newsList" style="width: 100%; height: 100%" stripe :show-header="false" size="small">
            <el-table-column width="70">
               <template #default="{ row }">
                  <el-tag size="small" :type="getImpactType(row.impact)" effect="dark" style="width: 100%; text-align: center;">{{ getImpactLabel(row.impact) }}</el-tag>
               </template>
            </el-table-column>
            <el-table-column prop="title" show-overflow-tooltip min-width="150">
              <template #default="{ row }">
                <div class="news-item">
                    <span class="news-title">{{ row.title }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="category" width="60" align="right">
               <template #default="{ row }">
                 <el-tag size="small" effect="plain">{{ getCategoryLabel(row.category) }}</el-tag>
               </template>
            </el-table-column>
            <el-table-column width="100" align="right">
                <template #default="{ row }">
                    <span class="news-time">{{ formatTime(row.published_at).split(' ')[1] }}</span>
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

    <!-- Indicator Settings Dialog -->
    <el-dialog v-model="settingsVisible" title="指标参数设置" width="400px">
      <el-form :model="indicatorSettings" label-width="120px">
        <el-divider content-position="left">KDJ 参数</el-divider>
        <el-form-item label="周期 (N)">
            <el-input-number v-model="indicatorSettings.KDJ.n" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="K 平滑 (M1)">
            <el-input-number v-model="indicatorSettings.KDJ.m1" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="D 平滑 (M2)">
            <el-input-number v-model="indicatorSettings.KDJ.m2" :min="1" :max="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="settingsVisible = false">取消</el-button>
          <el-button type="primary" @click="saveSettings">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '@/services/api'
import { formatChartTooltip, INDICATOR_EXPLANATIONS } from '@/utils/chartTooltip'
import { ElMessage } from 'element-plus'
import { Money, TrendCharts, Aim, Bell, Histogram, Timer, Plus, Delete, Reading, Setting, InfoFilled } from '@element-plus/icons-vue'

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null
const historyChartRef = ref<HTMLElement | null>(null)
let historyChart: echarts.ECharts | null = null
const historyRange = ref<'1d' | '1m' | '3m' | '6m' | '1y'>('1d')
const range = ref<'1m' | '5m' | '15m' | '1h' | '1d'>('1d')
const selectedIndicators = ref<string[]>(['MA'])
const latestIndicators = ref<any[]>([])
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

const settingsVisible = ref(false)
const indicatorSettings = reactive({
    KDJ: { n: 9, m1: 3, m2: 3 }
})

const openSettingsDialog = () => {
    settingsVisible.value = true
}

const saveSettings = () => {
    // Reload chart to apply new settings
    settingsVisible.value = false
    loadChart()
}

const getImpactType = (impact: string) => {
  if (impact === 'Bullish') return 'danger'
  if (impact === 'Bearish') return 'success'
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
  if (status.value.news_fetch) {
    list.push({
      name: '新闻采集',
      type: 'info',
      lastRun: formatTime(status.value.news_fetch.last_run),
      inserted: status.value.news_fetch.inserted ?? 0,
      totalRuns: status.value.news_fetch.total_runs ?? 0,
      error: status.value.news_fetch.error
    })
  }
  return list
})

const getChangeClass = (val: string) => {
  if (val.includes('+')) return 'text-up'
  if (val.includes('-')) return 'text-down'
  return ''
}

const initHistoryChart = () => {
  if (historyChartRef.value) {
    if (historyChart) {
      historyChart.dispose()
    }
    historyChart = echarts.init(historyChartRef.value)
  }
}

const loadHistoryChart = async () => {
  try {
    let timeframe = '1d'
    // If range is '1d', we want intraday data (e.g. 1m) to show a trend
    if (historyRange.value === '1d') {
        timeframe = '1m'
    }

    const { data } = await api.get('/market/history', {
      params: { symbol: 'XAUUSD', timeframe: timeframe, window: historyRange.value }
    })
    
    // Sort by TS
    data.sort((a: any, b: any) => new Date(a.ts).getTime() - new Date(b.ts).getTime())
    
    const dates = data.map((d: any) => d.ts)
    const values = data.map((d: any) => d.value)
    
    if (!historyChart && historyChartRef.value) initHistoryChart()
    
    if (historyChart) {
        const option: any = {
            tooltip: {
                trigger: 'axis',
                formatter: formatChartTooltip,
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                borderColor: '#eee',
                borderWidth: 1,
                textStyle: { color: '#333' },
                padding: 10,
                extraCssText: 'box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); border-radius: 4px;'
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: dates.map((d: string) => {
                    const date = new Date(d)
                    if (historyRange.value === '1d') {
                        // For intraday, show time only
                        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
                    }
                    return date.toLocaleDateString()
                })
            },
            yAxis: {
                type: 'value',
                scale: true
            },
            series: [
                {
                    name: 'Gold Close',
                    type: 'line',
                    smooth: true,
                    data: values,
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                          { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
                          { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
                        ])
                    },
                    itemStyle: { color: '#409EFF' }
                }
            ]
        }
        historyChart.setOption(option)
    }
  } catch (e) {
      console.error('Failed to load history chart', e)
  }
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
    // Use detailed history to get 'open' price as fallback
    const { data: historyData } = await api.get('/market/history/detailed', {
      params: { symbol: 'XAUUSD', timeframe: '1d', window: '1m' }
    })
    
    if (historyData && historyData.length > 0 && currentPrice > 0) {
      // Sort history by TS just in case
      historyData.sort((a: any, b: any) => new Date(a.ts).getTime() - new Date(b.ts).getTime())

      const lastPoint = historyData[historyData.length - 1]
      const lastPointDate = new Date(lastPoint.ts).toISOString().split('T')[0]
      
      // Determine "Today" based on latest real-time data timestamp, not local system time
      let todayStr = new Date().toISOString().split('T')[0]
      if (currentTime) {
          todayStr = currentTime.toISOString().split('T')[0]
      }
      
      let prevClose = 0
      
      // Check if the last history point is "Today" (Current Session)
      if (lastPointDate === todayStr) {
        if (historyData.length >= 2) {
          // If we have history, use yesterday's close
          prevClose = historyData[historyData.length - 2].close
        } else {
          // If no history (only today exists), use today's Open as fallback (Intraday Change)
          prevClose = lastPoint.open
        }
      } else {
        // Last point is NOT today (it's yesterday or older), so it IS the previous close
        prevClose = lastPoint.close
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
    const requests: string[] = []
    
    // Add default requests
    selectedIndicators.value.forEach(ind => {
        if (ind === 'KDJ') {
             // Construct custom KDJ name with parameters if they differ from default
            const { n, m1, m2 } = indicatorSettings.KDJ
            const kdjName = `KDJ_${n}_${m1}_${m2}`
            requests.push(`${kdjName}_K`, `${kdjName}_D`, `${kdjName}_J`)
        } else if (ind === 'MACD') {
            requests.push('MACD', 'MACD_DEA', 'MACD_HIST')
        } else {
            requests.push(ind)
        }
    })
    
    // Fetch indicators
    for (const req of requests) {
        // Skip KDJ if we just added components
        if (req === 'KDJ') continue;
        try {
            const { data } = await api.get('/indicator/history', {
                params: { symbol: 'XAUUSD', timeframe, name: req }
            })
            const map = new Map()
            data.forEach((d: any) => map.set(new Date(d.ts).getTime(), d.value))
            
            // Align with price dates
            const series = dates.map((d: string) => map.get(new Date(d).getTime()) || null)
            
            // Normalize key for data access
            if (req.includes('KDJ') && (req.endsWith('_K') || req.endsWith('_D') || req.endsWith('_J'))) {
                const suffix = req.split('_').pop() // K, D, or J
                indicatorsData[`KDJ_${suffix}`] = series
            } else {
                indicatorsData[req] = series
            }
        } catch (e) {
            console.error(`Failed to load ${req}`, e)
        }
    }

    if (!chart && chartRef.value) initChart()
    
    if (chart) {
        // Preserve current zoom level
        let zoomStart = 0
        let zoomEnd = 100
        
        const prevOption = chart.getOption() as any
        if (prevOption && prevOption.dataZoom && prevOption.dataZoom.length > 0) {
            zoomStart = prevOption.dataZoom[0].start
            zoomEnd = prevOption.dataZoom[0].end
        }

        const option: any = {
             tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'cross' },
                formatter: formatChartTooltip,
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                borderColor: '#eee',
                borderWidth: 1,
                textStyle: { color: '#333' },
                padding: 10,
                extraCssText: 'box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); border-radius: 4px;'
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
             dataZoom: [
                 { type: 'inside', xAxisIndex: [0, 1], start: zoomStart, end: zoomEnd }, 
                 { type: 'slider', xAxisIndex: [0, 1], start: zoomStart, end: zoomEnd }
             ],
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
        
        // SUPPORT/RESISTANCE -> Main Chart
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

        // Sub Chart Indicators
        let hasSubChart = false
        
        if (indicatorsData['MACD']) {
             hasSubChart = true
             // DIF
             option.series.push({
                 name: 'DIF',
                 type: 'line',
                 xAxisIndex: 1,
                 yAxisIndex: 1,
                 data: indicatorsData['MACD'],
                 smooth: true,
                 symbol: 'none',
                 lineStyle: { color: '#5470c6', width: 1.5 }
             })
             
             // DEA
             if (indicatorsData['MACD_DEA']) {
                 option.series.push({
                     name: 'DEA',
                     type: 'line',
                     xAxisIndex: 1,
                     yAxisIndex: 1,
                     data: indicatorsData['MACD_DEA'],
                     smooth: true,
                     symbol: 'none',
                     lineStyle: { color: '#e6a23c', width: 1.5 }
                 })
             }
             
             // Histogram
             if (indicatorsData['MACD_HIST']) {
                 option.series.push({
                     name: 'MACD',
                     type: 'bar',
                     xAxisIndex: 1,
                     yAxisIndex: 1,
                     data: indicatorsData['MACD_HIST'].map((v: number) => {
                         return {
                             value: v,
                             itemStyle: {
                                 color: v >= 0 ? '#ef232a' : '#14b143'
                             }
                         }
                     }),
                     barWidth: '50%'
                 })
             }
        }
        
        if (indicatorsData['RSI']) {
             hasSubChart = true
             option.series.push({
                 name: 'RSI',
                 type: 'line',
                 xAxisIndex: 1,
                 yAxisIndex: 1,
                 data: indicatorsData['RSI'],
                 smooth: true,
                 symbol: 'none',
                 markLine: {
                     data: [{ yAxis: 30 }, { yAxis: 70 }]
                 }
             })
        }
        
        if (indicatorsData['KDJ_K'] && indicatorsData['KDJ_D'] && indicatorsData['KDJ_J']) {
             hasSubChart = true
             option.series.push(
                 {
                     name: 'K',
                     type: 'line',
                     xAxisIndex: 1,
                     yAxisIndex: 1,
                     data: indicatorsData['KDJ_K'],
                     smooth: true,
                     symbol: 'none',
                     lineStyle: { width: 1, color: '#91cc75' }
                 },
                 {
                     name: 'D',
                     type: 'line',
                     xAxisIndex: 1,
                     yAxisIndex: 1,
                     data: indicatorsData['KDJ_D'],
                     smooth: true,
                     symbol: 'none',
                     lineStyle: { width: 1, color: '#fac858' }
                 },
                 {
                     name: 'J',
                     type: 'line',
                     xAxisIndex: 1,
                     yAxisIndex: 1,
                     data: indicatorsData['KDJ_J'],
                     smooth: true,
                     symbol: 'none',
                     lineStyle: { width: 1, color: '#ee6666' }
                 }
             )
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
        
        // Update Side Panel Info
        updateLatestIndicators(dates, values, indicatorsData)
    }
  } catch (e: any) {
    console.error('Load chart error:', e)
    ElMessage.error(e?.response?.data?.detail || '加载图表数据失败')
  }
}

const updateLatestIndicators = (dates: string[], values: any[], indicatorsData: any) => {
    const lastIndex = dates.length - 1
    if (lastIndex < 0) {
        latestIndicators.value = []
        return
    }
    
    // Helper to find last valid value in a series, looking back up to 5 points
    const getLastValidValue = (series: any[], currentIndex: number) => {
        if (!series) return null
        // Try current index first
        if (series[currentIndex] !== null && series[currentIndex] !== undefined) {
            return { value: series[currentIndex], index: currentIndex }
        }
        // Backtrack
        for (let i = 1; i <= 5; i++) {
            const idx = currentIndex - i
            if (idx >= 0 && series[idx] !== null && series[idx] !== undefined) {
                return { value: series[idx], index: idx }
            }
        }
        return null
    }
    
    const infos: any[] = []
    
    // 1. K-Line (Price)
    const kData = values[lastIndex]
    // [Open, Close, Low, High]
    if (kData && kData.length >= 2) {
        const close = kData[1]
        const open = kData[0]
        const change = close - open
        const changePct = (change / open) * 100
        const color = change >= 0 ? '#ef232a' : '#14b143'
        
        infos.push({
            name: 'Price',
            label: '最新价',
            value: `${Number(close).toFixed(2)}`,
            color: color,
            desc: `收盘价: ${Number(close).toFixed(2)}，涨跌: ${change >= 0 ? '+' : ''}${change.toFixed(2)} (${changePct.toFixed(2)}%)`
        })
    }
    
    // 2. MA
    const maData = getLastValidValue(indicatorsData['MA'], lastIndex)
    if (maData) {
        infos.push({
            name: 'MA',
            label: 'MA20',
            value: Number(maData.value).toFixed(2),
            color: '#5470c6',
            desc: INDICATOR_EXPLANATIONS['MA']
        })
    }
    
    // 3. MACD
    const macdData = getLastValidValue(indicatorsData['MACD'], lastIndex)
    if (macdData) {
        const idx = macdData.index
        const dif = Number(indicatorsData['MACD'][idx]).toFixed(3)
        let desc = INDICATOR_EXPLANATIONS['MACD']
        let val = `DIF: ${dif}`
        
        if (indicatorsData['MACD_DEA'] && indicatorsData['MACD_DEA'][idx] !== null) {
            const dea = Number(indicatorsData['MACD_DEA'][idx]).toFixed(3)
            val += ` / DEA: ${dea}`
        }
        if (indicatorsData['MACD_HIST'] && indicatorsData['MACD_HIST'][idx] !== null) {
             const hist = Number(indicatorsData['MACD_HIST'][idx]).toFixed(3)
             val += ` / MACD: ${hist}`
        }
        
        infos.push({
            name: 'MACD',
            label: 'MACD',
            value: val, 
            color: '#e6a23c',
            desc: desc
        })
    }
    
    // 4. RSI
    const rsiData = getLastValidValue(indicatorsData['RSI'], lastIndex)
    if (rsiData) {
        const rsi = Number(rsiData.value).toFixed(2)
        infos.push({
            name: 'RSI',
            label: 'RSI',
            value: rsi,
            color: '#91cc75',
            desc: INDICATOR_EXPLANATIONS['RSI']
        })
    }
    
    // 5. KDJ
    const kdjKData = getLastValidValue(indicatorsData['KDJ_K'], lastIndex)
    if (kdjKData) {
        const idx = kdjKData.index
        const k = Number(indicatorsData['KDJ_K'][idx]).toFixed(2)
        const d = (indicatorsData['KDJ_D'] && indicatorsData['KDJ_D'][idx] !== null) ? Number(indicatorsData['KDJ_D'][idx]).toFixed(2) : '-'
        const j = (indicatorsData['KDJ_J'] && indicatorsData['KDJ_J'][idx] !== null) ? Number(indicatorsData['KDJ_J'][idx]).toFixed(2) : '-'
        
        infos.push({
            name: 'KDJ',
            label: 'KDJ',
            value: `K:${k} D:${d} J:${j}`,
            color: '#ee6666',
            desc: INDICATOR_EXPLANATIONS['KDJ']
        })
    }
    
    // 6. Support/Resistance
    const supportData = getLastValidValue(indicatorsData['SUPPORT'], lastIndex)
    if (supportData) {
        infos.push({
            name: 'SUPPORT',
            label: '支撑位',
            value: Number(supportData.value).toFixed(2),
            color: '#14b143',
            desc: INDICATOR_EXPLANATIONS['SUPPORT']
        })
    }
    
    const resistanceData = getLastValidValue(indicatorsData['RESISTANCE'], lastIndex)
    if (resistanceData) {
        infos.push({
            name: 'RESISTANCE',
            label: '压力位',
            value: Number(resistanceData.value).toFixed(2),
            color: '#ef232a',
            desc: INDICATOR_EXPLANATIONS['RESISTANCE']
        })
    }
    
    latestIndicators.value = infos
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
  // Treat naive date strings as UTC
  let dateStr = t
  if (!dateStr.endsWith('Z') && !/[+-]\d{2}:?\d{2}/.test(dateStr)) {
    dateStr += 'Z'
  }
  return new Date(dateStr).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
}

let timer: any = null

onMounted(() => {
  nextTick(() => {
    initChart()
    loadChart()
    initHistoryChart()
    loadHistoryChart()
  })
  loadRealtimeStats()
  loadStatus()
  loadAlerts()
  loadForecast()
  loadNews()
  globalThis.addEventListener('resize', () => {
      if (chart) chart.resize()
      if (historyChart) historyChart.resize()
  })
  
  // Refresh data every 10 seconds to show real-time updates
  timer = setInterval(() => {
    if (range.value === '1d') {
        loadChart()
    }
    loadRealtimeStats()
    loadForecast()
    loadStatus()
    loadAlerts()
    loadNews()
    loadHistoryChart()
  }, 10000)
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
    chart = null
  }
  if (historyChart) {
    historyChart.dispose()
    historyChart = null
  }
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding-bottom: 20px;
}
.stat-card {
  display: flex;
  align-items: center;
  border: none;
  height: 100%;
  padding-left: 15px; /* Add left padding as requested */
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
  padding: 0; /* Will be overridden by inline style if important not used */
}
.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  padding: 20px;
  width: 100%;
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
}
.chart {
  width: 100%;
  height: 100%;
}
.chart-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}
.bottom-row {
  flex: 2;
  min-height: 0;
}
.news-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.news-title {
  font-weight: 500;
}
.news-time {
  font-size: 12px;
  color: #8c8c8c;
}

.chart-info-panel {
  width: 260px;
  padding: 15px;
  background: #f8f9fa;
  border-left: 1px solid #ebeef5;
  overflow-y: auto;
  font-size: 12px;
  display: flex;
  flex-direction: column;
}

.info-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #303133;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.info-list {
    flex: 1;
    overflow-y: auto;
}

.info-item {
  margin-bottom: 16px;
  padding: 8px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.info-label {
  font-weight: 600;
  font-size: 13px;
}

.info-value {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-weight: bold;
  color: #606266;
  font-size: 12px;
}

.info-desc {
  color: #909399;
  line-height: 1.5;
  font-size: 12px;
  text-align: justify;
}

.info-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #909399;
  text-align: center;
  padding: 20px;
}
</style>