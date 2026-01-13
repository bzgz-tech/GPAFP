<template>
  <div class="change-password-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">修改密码</h1>
        <p class="page-subtitle">定期修改密码以保护您的账户安全</p>
      </div>
    </div>

    <div class="content-wrapper">
      <el-card shadow="hover" class="password-card">
        <template #header>
          <div class="card-header">
            <span>密码修改</span>
          </div>
        </template>
        
        <el-form 
          :model="form" 
          :rules="rules" 
          ref="formRef" 
          label-width="100px" 
          size="large"
          status-icon
          class="password-form"
        >
          <el-form-item label="用户名">
            <el-input v-model="username" disabled :prefix-icon="User" />
          </el-form-item>
          
          <el-form-item label="旧密码" prop="oldPassword">
            <el-input 
              v-model="form.oldPassword" 
              type="password" 
              placeholder="请输入当前密码" 
              show-password 
              :prefix-icon="Lock" 
            />
          </el-form-item>
          
          <el-form-item label="新密码" prop="newPassword">
            <el-input 
              v-model="form.newPassword" 
              type="password" 
              placeholder="请输入新密码" 
              show-password 
              :prefix-icon="Lock" 
            />
          </el-form-item>
          
          <el-form-item label="确认新密码" prop="confirmNewPassword">
            <el-input 
              v-model="form.confirmNewPassword" 
              type="password" 
              placeholder="请再次输入新密码" 
              show-password 
              :prefix-icon="Lock" 
            />
          </el-form-item>
          
          <el-form-item label="验证码" prop="captchaCode">
            <div class="captcha-row">
              <el-input 
                v-model="captchaCode" 
                placeholder="请输入验证码" 
                :prefix-icon="Picture" 
              />
              <div class="captcha-img" @click="fetchCaptcha" title="点击刷新验证码">
                <img v-if="captchaUrl" :src="captchaUrl" alt="验证码" />
              </div>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="onSubmit">确认修改</el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store'
import api from '@/services/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Lock, Picture } from '@element-plus/icons-vue'
import { useCaptcha } from '@/composables/useCaptcha'

const router = useRouter()
const userStore = useUserStore()
const { captchaId, captchaUrl, captchaCode, fetchCaptcha } = useCaptcha()

const loading = ref(false)
const formRef = ref()

const username = computed(() => userStore.user?.username || '')

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmNewPassword: ''
})

const validatePass2 = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.newPassword) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const rules = {
  oldPassword: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { pattern: /^(?=.*[a-zA-Z])(?=.*\d).{8,}$/, message: '密码需至少8位，包含字母和数字', trigger: 'blur' }
  ],
  confirmNewPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ]
}

onMounted(() => {
  fetchCaptcha()
})

const onSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  
  if (!captchaCode.value) {
    ElMessage.warning('请输入验证码')
    return
  }
  
  loading.value = true
  try {
    await api.post('/auth/change-password', {
      username: username.value,
      old_password: form.oldPassword,
      new_password: form.newPassword,
      captcha_id: captchaId.value,
      captcha_code: captchaCode.value
    })
    
    ElMessageBox.alert('密码修改成功，请重新登录', '提示', {
      confirmButtonText: '确定',
      type: 'success',
      callback: () => {
        userStore.clearToken()
        router.push('/login')
      }
    })
  } catch (error: any) {
    const detail = error?.response?.data?.detail
    if (detail) {
      ElMessage.error(detail)
    } else {
      ElMessage.error('密码修改失败，请重试')
    }
    // Refresh captcha on error
    fetchCaptcha()
    captchaCode.value = ''
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
    captchaCode.value = ''
  }
}
</script>

<style scoped>
.change-password-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-color-secondary);
  margin: 0;
}

.content-wrapper {
  display: flex;
  justify-content: center;
}

.password-card {
  width: 100%;
  max-width: 600px;
  border-radius: 8px;
  border: none;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}

.password-form {
  padding: 20px 0;
}

.captcha-row {
  display: flex;
  gap: 12px;
}

.captcha-img {
  height: 40px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--border-color-base);
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-color-base);
  min-width: 120px;
}

.captcha-img img {
  height: 100%;
  width: auto;
  display: block;
}
</style>