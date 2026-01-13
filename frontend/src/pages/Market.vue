<template>
  <div class="market-page">
    <!-- K-Line Chart Section -->
    <el-card class="chart-card" shadow="never" style="margin-bottom: 20px;">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><Histogram /></el-icon>
            <span>专业K线图表</span>
          </div>
          <div class="chart-controls">
            <el-button type="primary" size="small" @click="handleAIAnalysis" :loading="aiLoading" style="margin-right: 10px;">
                <el-icon><Monitor /></el-icon> AI 智能分析
            </el-button>
            <el-checkbox-group v-model="selectedLinkage" size="small" @change="loadChart" style="margin-right: 10px">
              <el-checkbox-button label="DX-Y.NYB">美元</el-checkbox-button>
              <el-checkbox-button label="^TNX">美债</el-checkbox-button>
              <el-checkbox-button label="CL=F">原油</el-checkbox-button>
            </el-checkbox-group>

            <el-checkbox-group v-model="selectedIndicators" size="small" @change="loadChart">
              <el-checkbox-button label="MA">MA</el-checkbox-button>
              <el-checkbox-button label="MACD">MACD</el-checkbox-button>
              <el-checkbox-button label="RSI">RSI</el-checkbox-button>
              <el-checkbox-button label="KDJ">KDJ</el-checkbox-button>
              <el-checkbox-button label="SUPPORT">支撑</el-checkbox-button>
              <el-checkbox-button label="RESISTANCE">压力</el-checkbox-button>
            </el-checkbox-group>
            <el-radio-group v-model="range" size="small" @change="loadChart" style="margin-left: 10px;">
              <el-radio-button label="1m">1分</el-radio-button>
              <el-radio-button label="5m">5分</el-radio-button>
              <el-radio-button label="15m">15分</el-radio-button>
              <el-radio-button label="1h">1时</el-radio-button>
              <el-radio-button label="1d">日K</el-radio-button>
            </el-radio-group>
            <el-button link size="small" @click="openSettingsDialog" style="margin-left: 10px">
                <el-icon><Setting /></el-icon>
            </el-button>
            <el-dropdown split-button type="primary" size="small" @click="saveTemplate" @command="applyTemplate" style="margin-left: 10px">
              保存模板
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="t in savedTemplates" :key="t.name" :command="t">{{ t.name }}</el-dropdown-item>
                  <el-dropdown-item divided command="clear">重置</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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

    <!-- Historical Data Table Section -->
    <el-card shadow="never" class="market-card">
      <template #header>
        <div class="card-header">
          <div class="header-title">
             <el-icon><TrendCharts /></el-icon>
             <span>历史行情数据</span>
          </div>
          <div class="left">
            <el-form :inline="true" :model="filters" class="filter-form">
              <el-form-item label="品种">
                <el-select v-model="filters.symbol" placeholder="选择品种" style="width: 120px;">
                  <el-option label="XAUUSD" value="XAUUSD" />
                </el-select>
              </el-form-item>
              <el-form-item label="周期">
                <el-select v-model="filters.timeframe" placeholder="选择周期" style="width: 100px;">
                  <el-option label="日线" value="1d" />
                  <el-option label="小时线" value="1h" />
                  <el-option label="分钟线" value="1m" />
                </el-select>
              </el-form-item>
              <el-form-item label="区间">
                <el-select v-model="filters.window" placeholder="选择区间" style="width: 120px;">
                  <el-option label="最近一月" value="1m" />
                  <el-option label="最近三月" value="3m" />
                  <el-option label="最近一年" value="1y" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loadTableData({ resetPage: true })" :loading="tableLoading">
                  <el-icon><Search /></el-icon> 查询
                </el-button>
              </el-form-item>
              <el-form-item>
                 <el-button type="success" @click="exportCSV" :disabled="!tableData.length">
                   <el-icon><Download /></el-icon> 导出CSV
                 </el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </template>

      <el-table :data="tableData" style="width: 100%" v-loading="tableLoading" stripe border height="400">
        <el-table-column prop="ts" label="时间" min-width="160">
          <template #default="{ row }">
            {{ formatTime(row.ts) }}
          </template>
        </el-table-column>
        <el-table-column prop="open" label="开盘价 (¥)" min-width="120" align="right">
          <template #default="{ row }">{{ row.open.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="high" label="最高价 (¥)" min-width="120" align="right">
          <template #default="{ row }">{{ row.high.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="low" label="最低价 (¥)" min-width="120" align="right">
          <template #default="{ row }">{{ row.low.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="close" label="收盘价 (¥)" min-width="120" align="right">
          <template #default="{ row }">{{ row.close.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" min-width="120" align="right" />
      </el-table>
      <div class="pagination-container" style="margin-top: 15px; display: flex; justify-content: flex-end;">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalItems"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

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
          <el-button @click="settingsVisible = false">
            <el-icon><Close /></el-icon> 取消
          </el-button>
          <el-button type="primary" @click="saveSettings">
            <el-icon><Check /></el-icon> 确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- AI Report Dialog -->
    <el-dialog v-model="showAIReport" title="AI 市场分析报告" width="60%">
      <div class="ai-report-content" v-loading="aiLoading">
        <div v-if="aiReportContent" class="markdown-body" v-html="renderedReport"></div>
        <el-empty v-else description="暂无报告，请点击生成" />
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAIReport = false">
            <el-icon><Close /></el-icon> 关闭
          </el-button>
          <el-button type="primary" @click="fetchAIReport" :loading="aiLoading">
            <el-icon><Refresh /></el-icon> 重新生成
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import { marked } from 'marked'
import api from '@/services/api'
import { formatChartTooltip, INDICATOR_EXPLANATIONS } from '@/utils/chartTooltip'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, TrendCharts, Histogram, Setting, InfoFilled, Monitor, Search, Close, Check, Refresh } from '@element-plus/icons-vue'

// Configure marked
marked.setOptions({
  breaks: true,
  gfm: true
})

// --- Chart State ---
const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null
const range = ref<'1m' | '5m' | '15m' | '1h' | '1d'>('1d')
const selectedIndicators = ref<string[]>(['MA'])
const selectedLinkage = ref<string[]>([])
const showEvents = ref(false)
const savedTemplates = ref<any[]>([])
const latestIndicators = ref<any[]>([])
const settingsVisible = ref(false)
const indicatorSettings = reactive({
    KDJ: { n: 9, m1: 3, m2: 3 }
})
const MAJOR_EVENTS = [
    { date: '2020-03-16', name: '降息至0', desc: '疫情冲击' },
    { date: '2020-08-07', name: '历史新高', desc: '突破2075' },
    { date: '2022-03-16', name: '首次加息', desc: '紧缩周期' },
    { date: '2023-10-07', name: '巴以冲突', desc: '避险升温' },
    { date: '2024-09-18', name: '降息50BP', desc: '降息周期' }
]

// --- Table State ---
const tableLoading = ref(false)
const tableData = ref<any[]>([])
const totalItems = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const filters = reactive({
  symbol: 'XAUUSD',
  timeframe: '1d',
  window: '1m'
})

// --- AI Report State ---
const aiLoading = ref(false)
const showAIReport = ref(false)
const aiReportContent = ref('')
const renderedReport = computed(() => {
    if (!aiReportContent.value) return ''
    return marked.parse(aiReportContent.value)
})

// --- Chart Logic ---

const saveTemplate = () => {
    ElMessageBox.prompt('请输入模板名称', '保存模板', {
        confirmButtonText: '保存',
        cancelButtonText: '取消',
    }).then(({ value }) => {
        if (!value) return
        const tpl = {
            name: value,
            indicators: [...selectedIndicators.value],
            linkage: [...selectedLinkage.value]
        }
        savedTemplates.value.push(tpl)
        localStorage.setItem('analysisTemplates', JSON.stringify(savedTemplates.value))
        ElMessage.success('模板保存成功')
    }).catch(() => {})
}

const applyTemplate = (cmd: any) => {
    if (cmd === 'clear') {
        selectedIndicators.value = []
        selectedLinkage.value = []
    } else {
        selectedIndicators.value = [...cmd.indicators]
        selectedLinkage.value = cmd.linkage ? [...cmd.linkage] : []
    }
    loadChart()
}

const openSettingsDialog = () => {
    settingsVisible.value = true
}

const saveSettings = () => {
    settingsVisible.value = false
    loadChart()
}

const initChart = () => {
  if (chartRef.value) {
    if (chart) {
      chart.dispose()
    }
    chart = echarts.init(chartRef.value)
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
    
    priceData.sort((a: any, b: any) => new Date(a.ts).getTime() - new Date(b.ts).getTime())
    
    const dates = priceData.map((d: any) => d.ts)
    const values = priceData.map((d: any) => [d.open, d.close, d.low, d.high])
    
    // Fetch Indicators
    const indicatorsData: any = {}
    const requests: string[] = []
    
    selectedIndicators.value.forEach(ind => {
        if (ind === 'KDJ') {
            const { n, m1, m2 } = indicatorSettings.KDJ
            const kdjName = `KDJ_${n}_${m1}_${m2}`
            requests.push(`${kdjName}_K`, `${kdjName}_D`, `${kdjName}_J`)
        } else if (ind === 'MACD') {
            requests.push('MACD', 'MACD_DEA', 'MACD_HIST')
        } else {
            requests.push(ind)
        }
    })
    
    for (const req of requests) {
        if (req === 'KDJ') continue;
        try {
            const { data } = await api.get('/indicator/history', {
                params: { symbol: 'XAUUSD', timeframe, name: req }
            })
            const map = new Map()
            data.forEach((d: any) => map.set(new Date(d.ts).getTime(), d.value))
            const series = dates.map((d: string) => map.get(new Date(d).getTime()) || null)
            
            if (req.includes('KDJ') && (req.endsWith('_K') || req.endsWith('_D') || req.endsWith('_J'))) {
                const suffix = req.split('_').pop()
                indicatorsData[`KDJ_${suffix}`] = series
            } else {
                indicatorsData[req] = series
            }
        } catch (e) {
            console.error(`Failed to load ${req}`, e)
        }
    }

    // Fetch Linkage Data
    const linkageSeries = []
    const linkNameMap: any = { 'DX-Y.NYB': '美元指数', '^TNX': '美债收益率', 'CL=F': '原油' }
    if (selectedLinkage.value.length > 0) {
        for (const linkSym of selectedLinkage.value) {
            try {
                const { data: linkData } = await api.get('/market/history/detailed', {
                    params: { symbol: linkSym, timeframe, window: windowStr }
                })
                const map = new Map()
                linkData.forEach((d: any) => map.set(new Date(d.ts).getTime(), d.close))
                const series = dates.map((d: string) => map.get(new Date(d).getTime()) || null)
                const firstVal = series.find((v: any) => v !== null)
                const normalized = series.map((v: any) => v !== null && firstVal ? ((v - firstVal) / firstVal * 100) : null)
                
                linkageSeries.push({
                    name: linkNameMap[linkSym] || linkSym,
                    type: 'line',
                    yAxisIndex: 2,
                    showSymbol: false,
                    data: normalized,
                    smooth: true,
                    lineStyle: { width: 1.5 }
                })
            } catch (e) {
                console.error(`Failed to load linkage ${linkSym}`, e)
            }
        }
    }

    if (!chart && chartRef.value) initChart()
    
    if (chart) {
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
                 { 
                    type: 'category', 
                    data: dates, 
                    scale: true, 
                    boundaryGap: false, 
                    gridIndex: 0, 
                    axisLabel: { show: false } 
                 },
                 { 
                    type: 'category', 
                    data: dates, 
                    scale: true, 
                    boundaryGap: false, 
                    gridIndex: 1,
                    axisLabel: {
                        formatter: (val: string) => {
                            const d = new Date(val)
                            return `${d.getMonth()+1}-${d.getDate()} ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`
                        }
                    }
                 }
             ],
             yAxis: [
                 { scale: true, gridIndex: 0, splitLine: { show: false } },
                 { scale: true, gridIndex: 1, splitLine: { show: false } },
                 { 
                    show: selectedLinkage.value.length > 0,
                    scale: true, 
                    gridIndex: 0, 
                    position: 'right', 
                    splitLine: { show: false },
                    axisLabel: { formatter: '{value}%' },
                    name: '关联(%)'
                 }
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
                     },
                     markPoint: showEvents.value ? {
                         symbol: 'pin',
                         symbolSize: 40,
                         data: MAJOR_EVENTS.map(e => {
                             const idx = dates.findIndex((d: string) => d.startsWith(e.date))
                             if (idx === -1) return null
                             return {
                                 name: e.name,
                                 coord: [idx, values[idx][1]],
                                 value: e.name,
                                 label: { show: true, fontSize: 10 }
                             }
                         }).filter(x => x !== null)
                     } : undefined
                 },
                 ...linkageSeries
             ]
        }
        
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

        let hasSubChart = false
        
        if (indicatorsData['MACD']) {
             hasSubChart = true
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
             if (indicatorsData['MACD_HIST']) {
                 option.series.push({
                     name: 'MACD',
                     type: 'bar',
                     xAxisIndex: 1,
                     yAxisIndex: 1,
                     data: indicatorsData['MACD_HIST'].map((v: any) => ({
                         value: v,
                         itemStyle: { color: v >= 0 ? '#ef232a' : '#14b143' }
                     })),
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
            option.grid[0].height = '80%'
            option.grid[1].height = '0%'
            option.xAxis[0].axisLabel = { show: true }
            option.xAxis[1].show = false
            option.yAxis[1].show = false
        }
        
        chart.setOption(option, true)
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
    
    const getLastValidValue = (series: any[], currentIndex: number) => {
        if (!series) return null
        if (series[currentIndex] !== null && series[currentIndex] !== undefined) {
            return { value: series[currentIndex], index: currentIndex }
        }
        for (let i = 1; i <= 5; i++) {
            if (currentIndex - i >= 0 && series[currentIndex - i] !== null && series[currentIndex - i] !== undefined) {
                return { value: series[currentIndex - i], index: currentIndex - i }
            }
        }
        return null
    }

    const infos = []
    
    // MA
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
    
    // MACD
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
        infos.push({ name: 'MACD', label: 'MACD', value: val, color: '#e6a23c', desc: desc })
    }
    
    // RSI
    const rsiData = getLastValidValue(indicatorsData['RSI'], lastIndex)
    if (rsiData) {
        infos.push({ name: 'RSI', label: 'RSI', value: Number(rsiData.value).toFixed(2), color: '#91cc75', desc: INDICATOR_EXPLANATIONS['RSI'] })
    }
    
    // KDJ
    const kdjKData = getLastValidValue(indicatorsData['KDJ_K'], lastIndex)
    if (kdjKData) {
        const idx = kdjKData.index
        const k = Number(indicatorsData['KDJ_K'][idx]).toFixed(2)
        const d = (indicatorsData['KDJ_D'] && indicatorsData['KDJ_D'][idx] !== null) ? Number(indicatorsData['KDJ_D'][idx]).toFixed(2) : '-'
        const j = (indicatorsData['KDJ_J'] && indicatorsData['KDJ_J'][idx] !== null) ? Number(indicatorsData['KDJ_J'][idx]).toFixed(2) : '-'
        infos.push({ name: 'KDJ', label: 'KDJ', value: `K:${k} D:${d} J:${j}`, color: '#ee6666', desc: INDICATOR_EXPLANATIONS['KDJ'] })
    }
    
    // Support/Resistance
    const supportData = getLastValidValue(indicatorsData['SUPPORT'], lastIndex)
    if (supportData) {
        infos.push({ name: 'SUPPORT', label: '支撑位', value: Number(supportData.value).toFixed(2), color: '#14b143', desc: INDICATOR_EXPLANATIONS['SUPPORT'] })
    }
    const resistanceData = getLastValidValue(indicatorsData['RESISTANCE'], lastIndex)
    if (resistanceData) {
        infos.push({ name: 'RESISTANCE', label: '压力位', value: Number(resistanceData.value).toFixed(2), color: '#ef232a', desc: INDICATOR_EXPLANATIONS['RESISTANCE'] })
    }
    
    latestIndicators.value = infos
}

// --- AI Analysis Logic ---
const handleAIAnalysis = async () => {
    showAIReport.value = true
    if (!aiReportContent.value) {
        await fetchAIReport()
    }
}

const fetchAIReport = async () => {
    aiLoading.value = true
    aiReportContent.value = ''
    
    let startDate = ''
    let endDate = ''
    
    if (chart) {
        const option = chart.getOption() as any
        if (option && option.xAxis && option.xAxis[0] && option.xAxis[0].data) {
            const dates = option.xAxis[0].data
            const zoom = option.dataZoom ? option.dataZoom[0] : null
            if (dates.length > 0 && zoom) {
                const startPct = zoom.start
                const endPct = zoom.end
                const startIndex = Math.floor((dates.length - 1) * startPct / 100)
                const endIndex = Math.ceil((dates.length - 1) * endPct / 100)
                const safeStart = Math.max(0, Math.min(startIndex, dates.length - 1))
                const safeEnd = Math.max(0, Math.min(endIndex, dates.length - 1))
                startDate = dates[safeStart]
                endDate = dates[safeEnd]
            }
        }
    }

    try {
        const params: any = { symbol: 'XAUUSD', timeframe: range.value }
        if (startDate) params.start_date = startDate
        if (endDate) params.end_date = endDate
        const res = await api.get('/analysis/ai_report', { params, timeout: 120000 })
        aiReportContent.value = res.data.report
    } catch (err: any) {
        console.error(err)
        ElMessage.error('获取AI分析报告失败')
        aiReportContent.value = '分析服务暂时不可用，请稍后重试。'
    } finally {
        aiLoading.value = false
    }
}

// --- Table Logic ---
const loadTableData = async (options: { silent?: boolean, resetPage?: boolean } = {}) => {
  const { silent = false, resetPage = false } = options
  if (resetPage) {
      currentPage.value = 1
  }
  if (!silent) {
      tableLoading.value = true
  }
  try {
    const { data } = await api.get('/market/history/paged', {
      params: {
          ...filters,
          page: currentPage.value,
          page_size: pageSize.value
      }
    })
    tableData.value = data.items
    totalItems.value = data.total
  } catch (e: any) {
    if (!silent) ElMessage.error(e?.response?.data?.detail || '加载数据失败')
  } finally {
    tableLoading.value = false
  }
}

const handleSizeChange = () => {
    loadTableData({ resetPage: true })
}

const handleCurrentChange = () => {
    loadTableData()
}

const formatTime = (ts: string) => {
  return new Date(ts).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
}

const exportCSV = () => {
  if (!tableData.value.length) return
  const headers = ['时间', '开盘价', '最高价', '最低价', '收盘价', '成交量']
  const rows = tableData.value.map(row => [
    formatTime(row.ts),
    row.open,
    row.high,
    row.low,
    row.close,
    row.volume || 0
  ])
  const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `market_data_${filters.symbol}_${filters.timeframe}_${new Date().toISOString().slice(0,10)}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

let timer: any = null

onMounted(() => {
  const saved = localStorage.getItem('analysisTemplates')
  if (saved) {
      try {
          savedTemplates.value = JSON.parse(saved)
      } catch(e) {}
  }

  nextTick(() => {
    initChart()
    loadChart()
  })
  
  loadTableData()
  
  globalThis.addEventListener('resize', () => {
      if (chart) chart.resize()
  })

  timer = setInterval(() => {
      loadTableData({ silent: true })
      if (range.value === '1d' || range.value === '1m') { // Only auto refresh short intervals or daily
          loadChart()
      }
  }, 60000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  if (chart) {
      chart.dispose()
      chart = null
  }
})
</script>

<style scoped>
.market-page {
  /* No padding needed */
}
.chart-card, .market-card {
  border: none;
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
    align-items: center;
}
.filter-form {
  display: flex;
  margin-bottom: 0;
}
:deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 16px;
}

.chart-info-panel {
    width: 250px;
    padding-left: 20px;
    border-left: 1px solid #eee;
    overflow-y: auto;
}
.info-title {
    font-weight: bold;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 5px;
    color: #333;
}
.info-item {
    margin-bottom: 15px;
    padding: 10px;
    background-color: #f8f9fa;
    border-radius: 4px;
}
.info-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
}
.info-label {
    font-weight: bold;
}
.info-value {
    font-family: monospace;
}
.info-desc {
    font-size: 12px;
    color: #666;
    line-height: 1.4;
}
.info-empty {
    text-align: center;
    color: #999;
    margin-top: 50px;
}
</style>
