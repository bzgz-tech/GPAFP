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
            <span>{{ modeTitle }}</span>
          </div>
        </template>
        
        <!-- Login Form -->
        <el-form v-if="mode === 'login'" :model="form" :rules="rules" ref="formRef" size="large" @keyup.enter="onSubmit">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="密码" show-password :prefix-icon="Lock" />
          </el-form-item>
          <el-form-item>
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
              <el-button link type="primary" @click="mode = 'register'">注册账号</el-button>
              <el-divider direction="vertical" />
              <el-button link type="primary" @click="mode = 'change-password'">修改密码</el-button>
            </div>
          </div>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="onSubmit" class="submit-btn">登录</el-button>
          </el-form-item>
        </el-form>

        <!-- Register Form -->
        <el-form v-else-if="mode === 'register'" :model="registerForm" :rules="registerRules" ref="registerFormRef" size="large" @keyup.enter="onRegister">
          <el-form-item prop="username">
            <el-input v-model="registerForm.username" placeholder="用户名" :prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="registerForm.password" type="password" placeholder="密码" show-password :prefix-icon="Lock" />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input v-model="registerForm.confirmPassword" type="password" placeholder="确认密码" show-password :prefix-icon="Lock" />
          </el-form-item>
          <div class="form-actions right-align">
            <el-button link type="primary" @click="mode = 'login'">返回登录</el-button>
          </div>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="onRegister" class="submit-btn">注册</el-button>
          </el-form-item>
        </el-form>

        <!-- Change Password Form -->
        <el-form v-else :model="changePwdForm" :rules="changePwdRules" ref="changePwdFormRef" size="large" @keyup.enter="onChangePassword">
          <el-form-item prop="username">
            <el-input v-model="changePwdForm.username" placeholder="用户名" :prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="oldPassword">
            <el-input v-model="changePwdForm.oldPassword" type="password" placeholder="旧密码" show-password :prefix-icon="Lock" />
          </el-form-item>
          <el-form-item prop="newPassword">
            <el-input v-model="changePwdForm.newPassword" type="password" placeholder="新密码" show-password :prefix-icon="Lock" />
          </el-form-item>
          <el-form-item prop="confirmNewPassword">
            <el-input v-model="changePwdForm.confirmNewPassword" type="password" placeholder="确认新密码" show-password :prefix-icon="Lock" />
          </el-form-item>
          <el-form-item>
            <div class="captcha-row">
              <el-input v-model="changePwdCaptchaCode" placeholder="验证码" :prefix-icon="Picture" />
              <div class="captcha-img" @click="fetchCaptcha" title="点击刷新验证码">
                <img v-if="captchaUrl" :src="captchaUrl" alt="验证码" />
              </div>
            </div>
          </el-form-item>
          <div class="form-actions right-align">
            <el-button link type="primary" @click="mode = 'login'">返回登录</el-button>
          </div>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="onChangePassword" class="submit-btn">修改密码</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store'
import api from '@/services/api'
import { ElMessage } from 'element-plus'
import { User, Lock, GoldMedal, Picture } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// Captcha
const captchaUrl = ref('')
const captchaId = ref('')
const captchaCode = ref('')
const registerCaptchaCode = ref('')
const changePwdCaptchaCode = ref('')

const fetchCaptcha = async () => {
  try {
    const res = await api.get('/auth/captcha')
    captchaId.value = res.data.captcha_id
    captchaUrl.value = res.data.image
  } catch (error) {
    console.error('Failed to fetch captcha', error)
  }
}

// Mode: login, register, change-password
const mode = ref('login')

const modeTitle = computed(() => {
  switch (mode.value) {
    case 'register':
      return '注册账号'
    case 'change-password':
      return '修改密码'
    default:
      return '用户登录'
  }
})

// Login Form
const form = reactive({
  username: '',
  password: '',
})
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}
const formRef = ref()

// Register Form
const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})
const passwordStrengthRule = {
  pattern: /^(?=.*[a-zA-Z])(?=.*\d).{8,}$/,
  message: '密码需至少8位，包含字母和数字',
  trigger: 'blur'
}

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    passwordStrengthRule
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}
const registerFormRef = ref()

// Change Password Form
const changePwdForm = reactive({
  username: '',
  oldPassword: '',
  newPassword: '',
  confirmNewPassword: ''
})
const changePwdRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  oldPassword: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    passwordStrengthRule
  ],
  confirmNewPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== changePwdForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}
const changePwdFormRef = ref()

const loading = ref(false)
const remember = ref(true)

onMounted(() => {
  fetchCaptcha()
})

const onSubmit = async () => {
  if (formRef.value) {
    await formRef.value.validate()
  }
  if (!captchaCode.value) {
    ElMessage.warning('请输入验证码')
    return
  }
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('username', form.username)
    params.append('password', form.password)
    params.append('captcha_id', captchaId.value)
    params.append('captcha_code', captchaCode.value)
    
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
    ElMessage.error(error?.response?.data?.detail || '登录失败')
    fetchCaptcha()
    captchaCode.value = ''
  } finally {
    loading.value = false
  }
}

const onRegister = async () => {
  if (registerFormRef.value) {
    await registerFormRef.value.validate()
  }
  if (!registerCaptchaCode.value) {
    ElMessage.warning('请输入验证码')
    return
  }
  loading.value = true
  try {
    // Register user (email is optional/removed)
    await api.post('/auth/register', {
      username: registerForm.username,
      password: registerForm.password,
      email: null,
      captcha_id: captchaId.value,
      captcha_code: registerCaptchaCode.value
    })
    ElMessage.success('注册成功，请登录')
    mode.value = 'login'
    // Auto fill username
    form.username = registerForm.username
    // Refresh captcha
    fetchCaptcha()
    registerCaptchaCode.value = ''
    captchaCode.value = ''
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '注册失败')
    fetchCaptcha()
    registerCaptchaCode.value = ''
  } finally {
    loading.value = false
  }
}

const onChangePassword = async () => {
  if (changePwdFormRef.value) {
    await changePwdFormRef.value.validate()
  }
  if (!changePwdCaptchaCode.value) {
    ElMessage.warning('请输入验证码')
    return
  }
  loading.value = true
  try {
    await api.post('/auth/change-password', {
      username: changePwdForm.username,
      old_password: changePwdForm.oldPassword,
      new_password: changePwdForm.newPassword,
      captcha_id: captchaId.value,
      captcha_code: changePwdCaptchaCode.value
    })
    ElMessage.success('密码修改成功，请重新登录')
    mode.value = 'login'
    // Auto fill username
    form.username = changePwdForm.username
    // Refresh captcha
    fetchCaptcha()
    changePwdCaptchaCode.value = ''
    captchaCode.value = ''
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '修改密码失败')
    fetchCaptcha()
    changePwdCaptchaCode.value = ''
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

.form-actions.right-align {
  justify-content: flex-end;
}

.link-group {
  display: flex;
  align-items: center;
}

.submit-btn {
  width: 100%;
}

.submit-btn, .reset-btn {
  width: 100%;
}
</style>
