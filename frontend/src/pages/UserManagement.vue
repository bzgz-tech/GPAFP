<template>
  <div class="user-management">
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
    </div>
    
    <el-card shadow="hover">
      <el-table :data="users" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="is_admin" label="角色" width="120">
            <template #default="{ row }">
                <el-tag v-if="row.is_admin" type="danger" effect="dark">管理员</el-tag>
                <el-tag v-else type="info">普通用户</el-tag>
            </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '正常' : '已冻结' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180">
            <template #default="{ row }">
                {{ formatDate(row.created_at) }}
            </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.is_active" 
              type="danger" 
              size="small" 
              @click="toggleStatus(row)"
              :disabled="row.is_admin"
            >
              冻结
            </el-button>
            <el-button 
              v-else 
              type="success" 
              size="small" 
              @click="toggleStatus(row)"
            >
              解冻
            </el-button>
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
import api from '@/services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const users = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

const loadUsers = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/users/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    users.value = data.items
    total.value = data.total
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadUsers()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadUsers()
}

const toggleStatus = async (user: any) => {
  const action = user.is_active ? '冻结' : '解冻'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 ${user.username} 吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    
    await api.put(`/users/${user.id}/status`, {
      is_active: !user.is_active
    })
    
    ElMessage.success(`${action}成功`)
    loadUsers()
  } catch (e: any) {
    if (e !== 'cancel') {
        ElMessage.error(e.response?.data?.detail || `${action}失败`)
    }
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: 24px;
}
.page-title {
  font-size: 24px;
  margin: 0;
  color: #1f2f3d;
}
</style>
