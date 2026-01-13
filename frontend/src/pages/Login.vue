<template>
  <div class="login-container">
    <!-- Background Elements -->
    <div class="bg-shape shape-1"></div>
    <div class="bg-shape shape-2"></div>
    
    <div class="login-content">
      <!-- Left Side: Branding & Highlights -->
      <div class="login-left">
        <div class="brand-header">
          <img :src="logoUrl" class="brand-logo" alt="Logo" />
          <h1 class="brand-title">HJ价格分析与预测平台</h1>
        </div>
        
        <div class="slogan-container">
          <h2 class="slogan">数智金市 · 预见未来</h2>
          <p class="sub-slogan">AI 驱动的HJ投资决策引擎</p>
        </div>

        <div class="highlights">
          <div class="highlight-item" v-for="(item, index) in highlights" :key="index">
            <div class="highlight-icon-wrapper">
              <el-icon class="highlight-icon"><component :is="item.icon" /></el-icon>
            </div>
            <div class="highlight-text">
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </div>
        
        <div class="footer-copyright">
          © 2026 GPAFP. All Rights Reserved.
        </div>
      </div>

      <!-- Right Side: Login Form -->
      <div class="login-right">
        <div class="login-card">
          <div class="form-header">
            <h2>{{ modeTitle }}</h2>
            <p class="form-subtitle">{{ modeSubtitle }}</p>
          </div>
          
          <transition name="fade-slide" mode="out-in">
            <component 
              :is="currentComponent" 
              :initial-username="savedUsername"
              @switch-mode="handleSwitchMode" 
              @registered="handleRegistered"
              @password-changed="handlePasswordChanged"
            />
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, shallowRef } from 'vue'
import { Monitor, Cpu, TrendCharts, Bell } from '@element-plus/icons-vue'
import logoUrl from '@/assets/logo.svg'
import LoginForm from '@/components/auth/LoginForm.vue'
import RegisterForm from '@/components/auth/RegisterForm.vue'
import ChangePasswordForm from '@/components/auth/ChangePasswordForm.vue'

// Highlights Data
const highlights = [
  { icon: Monitor, title: '全维监控', desc: '实时行情秒级刷新，多周期 K 线深度洞察' },
  { icon: Cpu, title: 'AI 智脑', desc: '大模型生成深度研报，自动解读技术指标' },
  { icon: TrendCharts, title: '精准预测', desc: '机器学习算法预测走势，量化风险置信区间' },
  { icon: Bell, title: '风控哨兵', desc: '7*24 小时价格异动监测，关键点位实时告警' }
]

// Mode Management
const mode = ref('login')
const savedUsername = ref('')

const currentComponent = computed(() => {
  switch (mode.value) {
    case 'register': return RegisterForm
    case 'change-password': return ChangePasswordForm
    default: return LoginForm
  }
})

const modeTitle = computed(() => {
  switch (mode.value) {
    case 'register': return '注册账号'
    case 'change-password': return '修改密码'
    default: return '欢迎回来'
  }
})

const modeSubtitle = computed(() => {
  switch (mode.value) {
    case 'register': return '创建一个新账号以开始使用'
    case 'change-password': return '重置您的账户密码'
    default: return '请登录您的账号以继续'
  }
})

const handleSwitchMode = (newMode: string) => {
  mode.value = newMode
}

const handleRegistered = (username: string) => {
  savedUsername.value = username
}

const handlePasswordChanged = (username: string) => {
  savedUsername.value = username
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f0f2f5;
  position: relative;
  overflow: hidden;
  padding: 20px;
  box-sizing: border-box;
}

/* Background Shapes */
.bg-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 1;
  opacity: 0.15;
}

.shape-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(to right, #3b82f6, #60a5fa);
  top: -100px;
  right: -100px;
}

.shape-2 {
  width: 500px;
  height: 500px;
  background: linear-gradient(to right, #8b5cf6, #a78bfa);
  bottom: -150px;
  left: -150px;
  opacity: 0.1;
}

.login-content {
  display: flex;
  width: 100%;
  max-width: 1000px;
  height: 640px;
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  border: none;
  position: relative;
  z-index: 10;
  overflow: hidden;
}

/* Left Side */
.login-left {
  flex: 1.1;
  padding: 60px;
  display: flex;
  flex-direction: column;
  color: #fff;
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  position: relative;
}

.brand-header {
  display: flex;
  align-items: center;
  margin-bottom: 40px;
}

.brand-logo {
  width: 48px;
  height: 48px;
  margin-right: 16px;
  filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.3));
}

.brand-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  color: #fff;
  letter-spacing: 0.5px;
}

.slogan-container {
  margin-bottom: 60px;
}

.slogan {
  font-size: 42px;
  font-weight: 800;
  margin: 0 0 16px;
  background: linear-gradient(to right, #fbbf24, #f59e0b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1.2;
}

.sub-slogan {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-weight: 300;
}

.highlights {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.highlight-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  transition: transform 0.3s ease;
}

.highlight-item:hover {
  transform: translateX(8px);
}

.highlight-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.highlight-icon {
  font-size: 24px;
  color: #fbbf24;
}

.highlight-text h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 6px;
  color: rgba(255, 255, 255, 0.95);
}

.highlight-text p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  line-height: 1.5;
}

.footer-copyright {
  margin-top: auto;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
  text-align: center;
}

/* Right Side */
.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #ffffff;
  position: relative;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 0 20px;
}

.form-header {
  margin-bottom: 40px;
  text-align: center;
}

.form-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}

.form-subtitle {
  font-size: 15px;
  color: #64748b;
  margin: 0;
}

/* Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* Responsive */
@media (max-width: 960px) {
  .login-content {
    flex-direction: column;
    height: auto;
    max-width: 500px;
  }
  
  .login-left {
    padding: 40px;
  }
  
  .highlights {
    display: none;
  }
  
  .login-right {
    padding: 40px;
  }
}
</style>
