<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-header">
        <el-icon :size="48" class="logo-icon"><GoldMedal /></el-icon>
        <h1 class="app-title">黄金价格分析与预测平台</h1>
        <p class="app-subtitle">专业的市场数据分析与趋势预测工具</p>
      </div>
      
      <el-card class="login-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>用户登录</span>
          </div>
        </template>
        <el-form :model="form" :rules="rules" ref="formRef" size="large" @keyup.enter="onSubmit">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="密码" show-password :prefix-icon="Lock" />
          </el-form-item>
          <div class="form-actions">
            <el-checkbox v-model="remember">记住我</el-checkbox>
            <el-button link type="primary">忘记密码？</el-button>
          </div>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="onSubmit" class="submit-btn">登录</el-button>
          </el-form-item>
          <el-form-item>
            <el-button @click="onReset" class="reset-btn">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store'
import api from '@/services/api'
import { ElMessage } from 'element-plus'
import { User, Lock, GoldMedal } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const form = reactive({
  username: '',
  password: '',
})
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}
const formRef = ref()
const loading = ref(false)
const remember = ref(true)

const onSubmit = async () => {
  if (formRef.value) {
    await formRef.value.validate()
  }
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('username', form.username)
    formData.append('password', form.password)
    const response = await api.post('/auth/login', formData)
    userStore.setToken(response.data.access_token)
    if (!remember.value) {
      sessionStorage.setItem('token', response.data.access_token)
    }
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

const onReset = () => {
  form.username = ''
  form.password = ''
  if (formRef.value) {
    formRef.value.resetFields()
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
  background-image: url("data:image/svg+xml,%3Csvg width='64' height='64' viewBox='0 0 64 64' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M8 16c4.418 0 8-3.582 8-8s-3.582-8-8-8-8 3.582-8 8 3.582 8 8 8zm0-2c3.314 0 6-2.686 6-6s-2.686-6-6-6-6 2.686-6 6 2.686 6 6 6zm33.414-6l5.95-5.95L45.95.636 40 6.586 34.05.636 32.636 2.05 38.586 8l-5.95 5.95 1.414 1.414L40 9.414l5.95 5.95 1.414-1.414L41.414 8zM40 48c4.418 0 8-3.582 8-8s-3.582-8-8-8-8 3.582-8 8 3.582 8 8 8zm0-2c3.314 0 6-2.686 6-6s-2.686-6-6-6-6 2.686-6 6 2.686 6 6 6zM9.414 40l5.95-5.95-1.414-1.414L8 38.586l-5.95-5.95L.636 34.05 6.586 40l-5.95 5.95 1.414 1.414L8 41.414l5.95 5.95 1.414-1.414L9.414 40z' fill='%239C92AC' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
}

.login-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

.login-header {
  text-align: center;
}

.logo-icon {
  color: #faad14;
  margin-bottom: 16px;
}

.app-title {
  font-size: 32px;
  font-weight: 600;
  color: #000000d9;
  margin: 0 0 8px;
}

.app-subtitle {
  font-size: 14px;
  color: #00000073;
  margin: 0;
}

.login-card {
  width: 400px;
  border-radius: 8px;
}

.card-header {
  text-align: center;
  font-size: 18px;
  font-weight: 500;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.submit-btn, .reset-btn {
  width: 100%;
}
</style>
