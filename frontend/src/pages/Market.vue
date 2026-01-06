<template>
  <div class="market-page">
    <el-card shadow="never" class="market-card">
      <template #header>
        <div class="card-header">
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
                <el-button type="primary" @click="fetchData" :loading="loading">查询</el-button>
              </el-form-item>
            </el-form>
          </div>
          <div class="right">
            <el-button type="success" @click="exportCSV" :disabled="!tableData.length">
              <el-icon><Download /></el-icon> 导出CSV
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="tableData" style="width: 100%" v-loading="loading" stripe border height="600">
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
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import api from '@/services/api'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'

const loading = ref(false)
const tableData = ref<any[]>([])
const filters = reactive({
  symbol: 'XAUUSD',
  timeframe: '1d',
  window: '1m'
})

const fetchData = async (silent = false) => {
  if (!silent) loading.value = true
  try {
    const { data } = await api.get('/market/history/detailed', {
      params: filters
    })
    tableData.value = data
  } catch (e: any) {
    if (!silent) ElMessage.error(e?.response?.data?.detail || '加载数据失败')
  } finally {
    loading.value = false
  }
}

let timer: any = null

onMounted(() => {
  fetchData()
  timer = setInterval(() => fetchData(true), 60000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})

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
  
  const csvContent = [
    headers.join(','),
    ...rows.map(r => r.join(','))
  ].join('\n')
  
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `market_data_${filters.symbol}_${filters.timeframe}_${new Date().toISOString().slice(0,10)}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.market-page {
  /* No padding needed */
}
.market-card {
  border: none;
}
.card-header {
  display: flex;
  justify-content: space-between;
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
</style>
