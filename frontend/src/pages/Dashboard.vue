<template>
  <div class="dashboard">
    <el-row :gutter="24" class="top-row">
      <el-col :span="8">
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
      <el-col :span="8">
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
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon-wrapper forecast">
            <el-icon><Aim /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-title">
                AI预测 (7日)
                <el-popover placement="bottom" title="7日预测 (ARIMA)" :width="320" trigger="hover">
                    <template #reference>
                      <el-icon style="margin-left: 5px; cursor: pointer"><InfoFilled /></el-icon>
                    </template>
                    <el-table :data="forecastList" size="small" stripe>
                        <el-table-column property="date" label="日期" width="100"></el-table-column>
                        <el-table-column property="range" label="预测区间 (元/克)"></el-table-column>
                        <el-table-column property="accuracy" label="置信度" width="80">
                          <template #default="scope">
                            <el-tag size="small" type="success">{{ scope.row.accuracy }}</el-tag>
                          </template>
                        </el-table-column>
                    </el-table>
                </el-popover>
            </div>
            <div class="stat-value">{{ nextDayForecast }} <span class="unit">元/克</span></div>
            <div class="stat-time" v-if="forecastTime" style="font-size: 10px;">{{ forecastTime }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Historical Price Chart -->
    <el-card class="chart-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><TrendCharts /></el-icon>
            <span>近期市场走势</span>
          </div>
          <div class="header-actions">
            <el-radio-group v-model="chartTimeRange" size="small" @change="handleRangeChange" style="margin-right: 15px">
              <el-radio-button label="1d">1天</el-radio-button>
              <el-radio-button label="7d">1周</el-radio-button>
              <el-radio-button label="1m">1月</el-radio-button>
              <el-radio-button label="3m">3月</el-radio-button>
              <el-radio-button label="6m">6月</el-radio-button>
              <el-radio-button label="1y">1年</el-radio-button>
            </el-radio-group>
            <el-button type="primary" link @click="$router.push('/analysis')">
              查看深度分析报告 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </template>
      <div ref="historyChartRef" class="chart"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import api from '@/services/api'
import { formatChartTooltip } from '@/utils/chartTooltip'
import { Money, TrendCharts, Aim, InfoFilled, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()
const historyChartRef = ref<HTMLElement | null>(null)
let historyChart: echarts.ECharts | null = null

const chartTimeRange = ref('1m')

const latestDisplay = ref('—')
const latestTime = ref('')
const nextDayForecast = ref('—')
const forecastTime = ref('')
const forecastList = ref<any[]>([])
const dailyChange = ref('—')
const dailyChangeTime = ref('')

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

const handleRangeChange = () => {
    loadHistoryChart()
}

const loadHistoryChart = async () => {
  if (!historyChart && historyChartRef.value) initHistoryChart()
  historyChart?.showLoading()
  try {
    let timeframe = '1d'
    const window = chartTimeRange.value
    
    switch(window) {
        case '1d': timeframe = '30m'; break;
        case '7d': timeframe = '4h'; break;
        case '1m': timeframe = '1d'; break;
        case '3m': timeframe = '1d'; break;
        case '6m': timeframe = '1d'; break;
        case '1y': timeframe = '1w'; break;
    }

    const { data } = await api.get('/market/history/detailed', {
      params: { symbol: 'XAUUSD', timeframe, window }
    })
    
    historyChart?.hideLoading()

    if (!data || data.length === 0) {
        historyChart?.setOption({
            title: {
                text: '暂无数据',
                left: 'center',
                top: 'center',
                textStyle: { color: '#909399' }
            },
            series: []
        }, true)
        return
    }

    // Sort by TS ascending
    data.sort((a: any, b: any) => new Date(a.ts).getTime() - new Date(b.ts).getTime())
    
    const dates = data.map((d: any) => d.ts)
    const values = data.map((d: any) => d.close)
    
    if (historyChart) {
        const option: any = {
            tooltip: {
                trigger: 'axis',
                formatter: formatChartTooltip,
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                borderColor: '#e4e7ed',
                borderWidth: 1,
                textStyle: { color: '#303133' },
                padding: 12,
                extraCssText: 'box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1); border-radius: 4px;'
            },
            grid: {
                left: '2%',
                right: '3%',
                bottom: '5%',
                top: '5%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                axisLine: { lineStyle: { color: '#DCDFE6' } },
                axisLabel: { color: '#909399' },
                data: dates.map((d: string) => {
                    const date = new Date(d)
                    return date.toLocaleDateString()
                })
            },
            yAxis: {
                type: 'value',
                scale: true,
                axisLine: { show: false },
                axisTick: { show: false },
                splitLine: { lineStyle: { type: 'dashed', color: '#E4E7ED' } },
                axisLabel: { color: '#909399' }
            },
            series: [
                {
                    name: 'Gold Close',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    lineStyle: { width: 3, color: '#409EFF' },
                    data: values,
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(64, 158, 255, 0.2)' },
                            { offset: 1, color: 'rgba(64, 158, 255, 0.02)' }
                        ])
                    },
                    itemStyle: { color: '#409EFF' }
                }
            ]
        }
        historyChart.setOption(option, true)
    }
  } catch (e) {
      console.error('Failed to load history chart', e)
      historyChart?.hideLoading()
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
    
    // 3. AI Forecast (Mock/API)
    // Try to get AI forecast, fallback to mock if API fails or not ready
    try {
        const { data: forecastData } = await api.get('/analysis/forecast', {
            params: { symbol: 'XAUUSD', days: 7 }
        })
        if (forecastData && forecastData.length > 0) {
            nextDayForecast.value = Number(forecastData[0].price).toFixed(2)
            forecastTime.value = `预测日期: ${forecastData[0].date}`
            forecastList.value = forecastData.map((f: any) => ({
                date: f.date,
                range: `${Number(f.low).toFixed(2)} - ${Number(f.high).toFixed(2)}`,
                accuracy: f.confidence || 'High'
            }))
        }
    } catch (e) {
        // Fallback Mock
        nextDayForecast.value = (Number(currentPrice) * 1.002).toFixed(2)
        forecastTime.value = 'AI模型计算中...'
    }

  } catch (e) {
    console.error('Load realtime stats error:', e)
  }
}

let timer: any = null

onMounted(() => {
  initHistoryChart()
  loadHistoryChart()
  loadRealtimeStats()
  
  // Refresh real-time stats every 10s
  timer = setInterval(() => {
      loadRealtimeStats()
  }, 10000)
  
  window.addEventListener('resize', () => {
      historyChart?.resize()
  })
})

onUnmounted(() => {
    if (timer) clearInterval(timer)
    historyChart?.dispose()
    window.removeEventListener('resize', () => {})
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
}

.top-row {
  margin-bottom: 24px;
}

.stat-card {
  height: 180px; /* Increased height */
  border-radius: 12px;
  border: none;
  background: #ffffff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  overflow: hidden;
  position: relative;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.stat-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100%;
  background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.4) 100%);
  transform: skewX(-20deg) translateX(150%);
  transition: transform 0.6s;
}

.stat-card:hover::after {
  transform: skewX(-20deg) translateX(0);
}

/* Allow flex layout inside card body */
:deep(.el-card__body) {
    display: flex;
    align-items: center;
    width: 100%;
    height: 100%;
    padding: 32px;
    box-sizing: border-box;
}

.stat-icon-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 28px;
  font-size: 36px;
  color: white;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.05);
}

.money { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); }
.trend { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); }
.forecast { background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); }

.stat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.stat-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  line-height: 1.1;
  font-family: 'DIN Alternate', 'Roboto', sans-serif; /* Try to use a better number font */
}

.unit {
  font-size: 14px;
  font-weight: normal;
  color: #909399;
  margin-left: 6px;
  vertical-align: baseline;
}

.stat-time {
  font-size: 12px;
  color: #C0C4CC;
  margin-top: 8px;
}

.stat-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.text-up { color: #f56c6c; font-weight: bold; }
.text-down { color: #67c23a; font-weight: bold; }

.chart-card {
  border-radius: 8px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.chart {
  height: 450px;
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.header-title {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-title .el-icon {
  margin-right: 8px;
  font-size: 20px;
  color: #409EFF;
}
</style>
