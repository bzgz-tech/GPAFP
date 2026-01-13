<template>
  <div class="news-page">
    <el-card shadow="never" class="news-card">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><Reading /></el-icon>
            <span>市场资讯</span>
          </div>
          <el-tag size="small" type="info">实时聚合</el-tag>
        </div>
      </template>
      <div class="toolbar">
        <el-button type="primary" :icon="Refresh" @click="loadNews" :loading="loading">刷新</el-button>
      </div>
      <el-table :data="newsList" style="width: 100%" stripe :show-header="false" size="medium" v-loading="loading">
        <el-table-column width="80">
           <template #default="{ row }">
              <el-tag size="small" :type="getImpactType(row.impact)" effect="dark" style="width: 100%; text-align: center;">{{ getImpactLabel(row.impact) }}</el-tag>
           </template>
        </el-table-column>
        <el-table-column prop="title" show-overflow-tooltip min-width="300">
          <template #default="{ row }">
            <div class="news-item-content">
                <span class="news-title">{{ row.title }}</span>
                <span class="news-content" v-if="row.content">{{ row.content.substring(0, 100) }}...</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" width="100" align="right">
           <template #default="{ row }">
             <el-tag size="small" effect="plain">{{ getCategoryLabel(row.category) }}</el-tag>
           </template>
        </el-table-column>
        <el-table-column width="150" align="right">
            <template #default="{ row }">
                <span class="news-time">{{ formatTime(row.published_at) }}</span>
            </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container" style="margin-top: 15px; display: flex; justify-content: flex-end;">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Reading, Refresh } from '@element-plus/icons-vue'
import api from '@/services/api'
import { ElMessage } from 'element-plus'

const newsList = ref<any[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadNews = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/news/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    newsList.value = data.items
    total.value = data.total
  } catch (e) {
    console.error('Load news error', e)
    ElMessage.error('获取新闻失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadNews()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadNews()
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

const formatTime = (t: string | null | undefined) => {
  if (!t) return '—'
  // Treat naive date strings as UTC
  let dateStr = t
  if (!dateStr.endsWith('Z') && !/[+-]\d{2}:?\d{2}/.test(dateStr)) {
    dateStr += 'Z'
  }
  return new Date(dateStr).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
}

onMounted(() => {
  loadNews()
})
</script>

<style scoped>
.news-page {
  padding: 20px;
  height: 100%;
}
.news-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.news-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
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
.toolbar {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}
.news-item-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.news-title {
  font-weight: 500;
  font-size: 14px;
  color: #303133;
}
.news-content {
  font-size: 12px;
  color: #909399;
}
.news-time {
  font-size: 12px;
  color: #909399;
}
</style>
