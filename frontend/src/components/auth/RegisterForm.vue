<template>
  <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" size="large" @keyup.enter="onRegister" class="auth-form">
    <el-form-item prop="username">
      <el-input v-model="registerForm.username" placeholder="用户名" :prefix-icon="User" />
    </el-form-item>
    <el-form-item prop="password">
      <el-input v-model="registerForm.password" type="password" placeholder="密码" show-password :prefix-icon="Lock" />
    </el-form-item>
    <el-form-item prop="confirmPassword">
      <el-input v-model="registerForm.confirmPassword" type="password" placeholder="确认密码" show-password :prefix-icon="Lock" />
    </el-form-item>
    <el-form-item>
      <div class="captcha-row">
        <el-input v-model="captchaCode" placeholder="验证码" :prefix-icon="Picture" />
        <div class="captcha-img" @click="fetchCaptcha" title="点击刷新验证码">
          <img v-if="captchaUrl" :src="captchaUrl" alt="验证码" />
        </div>
      </div>
    </el-form-item>
    <div class="form-actions right-align">
      <el-button link type="primary" @click="$emit('switch-mode', 'login')">返回登录</el-button>
    </div>
    <el-form-item>
      <el-button type="primary" :loading="loading" @click="onRegister" class="submit-btn">注册</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import api from '@/services/api'
import { ElMessage } from 'element-plus'
import { User, Lock, Picture } from '@element-plus/icons-vue'
import { useCaptcha } from '@/composables/useCaptcha'

const emit = defineEmits(['switch-mode', 'registered'])
const { captchaId, captchaUrl, captchaCode, fetchCaptcha } = useCaptcha()

const loading = ref(false)
const registerFormRef = ref()

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

const validatePass2 = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    passwordStrengthRule
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ]
}

onMounted(() => {
  fetchCaptcha()
})

const onRegister = async () => {
  if (!registerFormRef.value) return
  await registerFormRef.value.validate()
  
  if (!captchaCode.value) {
    ElMessage.warning('请输入验证码')
    return
  }
  
  loading.value = true
  try {
    await api.post('/auth/register', {
      username: registerForm.username,
      password: registerForm.password,
      email: null,
      captcha_id: captchaId.value,
      captcha_code: captchaCode.value
    })
    ElMessage.success('注册成功，请登录')
    emit('registered', registerForm.username)
    emit('switch-mode', 'login')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '注册失败')
    fetchCaptcha()
    captchaCode.value = ''
  } finally {
    loading.value = false
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

.form-actions.right-align {
  justify-content: flex-end;
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
