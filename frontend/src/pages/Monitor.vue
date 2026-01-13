<template>
  <div class="monitor-page">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="never" class="monitor-card">
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
          <el-table :data="alerts" style="width: 100%" stripe empty-text="暂无活跃告警" size="medium" v-loading="loadingAlerts">
            <el-table-column prop="name" label="名称" show-overflow-tooltip />
            <el-table-column label="条件" width="120">
              <template #default="{ row }">
                <span :class="row.condition === 'price_above' ? 'text-up' : 'text-down'">
                    {{ row.condition === 'price_above' ? '≥' : '≤' }} {{ row.threshold }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
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
          <div class="pagination-container" style="margin-top: 15px; display: flex; justify-content: flex-end;">
            <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[5, 10, 20]"
                layout="total, sizes, prev, pager, next, jumper"
                :total="total"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
                small
            />
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="monitor-card">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon><Timer /></el-icon>
                <span>采集状态</span>
              </div>
              <el-tag size="small" type="success">正常运行</el-tag>
            </div>
          </template>
          <el-table :data="taskList" style="width: 100%" stripe size="medium" v-loading="loadingStatus">
            <el-table-column prop="name" label="任务" show-overflow-tooltip />
            <el-table-column label="上次运行" width="160">
              <template #default="{ row }">
                <span :class="row.error ? 'text-danger' : ''">{{ row.lastRun }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="inserted" label="新增数据" width="100" align="center" />
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
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { Bell, Timer, Plus, Delete } from '@element-plus/icons-vue'
import api from '@/services/api'
import { ElMessage } from 'element-plus'

const alerts = ref<any[]>([])
const status = ref<any>({})
const loadingAlerts = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loadingStatus = ref(false)
const dialogVisible = ref(false)
const creating = ref(false)

const alertForm = reactive({
  name: '',
  symbol: 'XAUUSD',
  condition: 'price_above',
  threshold: 0
})

const loadAlerts = async () => {
  loadingAlerts.value = true
  try {
    const { data } = await api.get('/alert/active', {
      params: {
        symbol: 'XAUUSD',
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    alerts.value = data.items
    total.value = data.total
  } catch (e) {
    console.error('Load alerts error', e)
    ElMessage.error('获取告警失败')
  } finally {
    loadingAlerts.value = false
  }
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadAlerts()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadAlerts()
}

const loadStatus = async () => {
  loadingStatus.value = true
  try {
    const { data } = await api.get('/tasks/status')
    status.value = data
  } catch {
    status.value = {}
  } finally {
    loadingStatus.value = false
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
  let dateStr = t
  if (!dateStr.endsWith('Z') && !/[+-]\d{2}:?\d{2}/.test(dateStr)) {
    dateStr += 'Z'
  }
  return new Date(dateStr).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
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

let timer: any = null

onMounted(() => {
  loadAlerts()
  loadStatus()
  
  // Refresh every 10 seconds
  timer = setInterval(() => {
      loadAlerts()
      loadStatus()
  }, 10000)
})

onUnmounted(() => {
    if (timer) {
        clearInterval(timer)
        timer = null
    }
})
</script>

<style scoped>
.monitor-page {
  padding: 20px;
}
.monitor-card {
  margin-bottom: 20px;
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
.text-up { color: #f5222d; }
.text-down { color: #52c41a; }
.text-danger { color: #f5222d; }
</style>
