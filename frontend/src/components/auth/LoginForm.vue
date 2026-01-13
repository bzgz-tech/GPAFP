<template>
  <el-form :model="form" :rules="rules" ref="formRef" size="large" @keyup.enter="onSubmit" class="auth-form">
    <el-form-item prop="username">
      <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
    </el-form-item>
    <el-form-item prop="password">
      <el-input v-model="form.password" type="password" placeholder="密码" show-password :prefix-icon="Lock" />
    </el-form-item>
    <el-form-item v-if="showCaptcha">
      <div class="captcha-row">
        <el-input v-model="captchaCode" placeholder="验证码" :prefix-icon="Picture" />
        <div class="captcha-img" @click="fetchCaptcha" title="点击刷新验证码">
          <img v-if="captchaUrl" :src="captchaUrl" alt="验证码" />
        </div>
      </div>
    </el-form-item>
    <div class="form-actions">
      <el-checkbox v-model="remember">记住我</el-checkbox>
      <div class="link-group">
        <el-button link type="primary" @click="$emit('switch-mode', 'register')">注册账号</el-button>
        <el-divider direction="vertical" />
        <el-button link type="primary" @click="$emit('switch-mode', 'change-password')">修改密码</el-button>
      </div>
    </div>
    <el-form-item>
      <el-button type="primary" :loading="loading" @click="onSubmit" class="submit-btn">登录</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store'
import api from '@/services/api'
import { ElMessage } from 'element-plus'
import { User, Lock, Picture } from '@element-plus/icons-vue'
import { useCaptcha } from '@/composables/useCaptcha'

const props = defineProps<{
  initialUsername?: string
}>()

defineEmits(['switch-mode'])

const router = useRouter()
const userStore = useUserStore()
const { captchaId, captchaUrl, captchaCode, fetchCaptcha } = useCaptcha()

const loading = ref(false)
const showCaptcha = ref(false)
const remember = ref(false)
const formRef = ref()

const form = reactive({
  username: props.initialUsername || '',
  password: '',
})

watch(() => props.initialUsername, (newVal) => {
  if (newVal) {
    form.username = newVal
  }
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const onSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  
  if (showCaptcha.value && !captchaCode.value) {
    ElMessage.warning('请输入验证码')
    return
  }
  
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('username', form.username)
    params.append('password', form.password)
    if (showCaptcha.value) {
      params.append('captcha_id', captchaId.value)
      params.append('captcha_code', captchaCode.value)
    }
    
    const response = await api.post('/auth/login', params)
    userStore.setToken(response.data.access_token)
    if (!remember.value) {
      sessionStorage.setItem('token', response.data.access_token)
    }
    // Fetch user info
    await userStore.fetchUser()
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error: any) {
    loading.value = false
    const detail = error?.response?.data?.detail
    if (error?.response?.status === 400 && detail === 'Require Captcha') {
      showCaptcha.value = true
      fetchCaptcha()
      ElMessage.warning('为了您的账号安全，请输入验证码')
    } else {
      ElMessage.error(detail || '登录失败')
      if (showCaptcha.value) {
        fetchCaptcha()
        captchaCode.value = ''
      }
    }
  }
}
</script>

<style scoped>
.auth-form {
  width: 100%;
  max-width: 360px;
  margin: 0 auto;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.link-group {
  display: flex;
  align-items: center;
}

.submit-btn {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  border-radius: 8px;
  height: 44px;
  background: linear-gradient(to right, #2563eb, #1d4ed8);
  border: none;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background: linear-gradient(to right, #1d4ed8, #1e40af);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.captcha-row {
  display: flex;
  gap: 12px;
}

.captcha-img {
  width: 120px;
  height: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9fafb;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
}

.captcha-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Input Styles */
:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #e5e7eb inset;
  padding: 1px 15px;
  border-radius: 8px;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #2563eb inset !important;
}
</style>
