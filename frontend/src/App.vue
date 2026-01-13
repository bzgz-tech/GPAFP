<template>
  <div id="app">
    <el-container v-if="isAuthed" class="layout-container">
      <el-header class="app-header">
        <div class="left">
          <div class="logo">
            <img :src="logoUrl" class="logo-icon" alt="Logo" />
            <span class="brand">黄金分析平台</span>
          </div>
          <el-menu
            mode="horizontal"
            router
            :ellipsis="false"
            :default-active="activePath"
            background-color="var(--color-header-bg)"
            text-color="var(--color-menu-text)"
            active-text-color="var(--color-menu-active-text)"
            class="nav-menu"
          >
            <el-menu-item index="/">
              <el-icon><Odometer /></el-icon>
              <span>仪表盘</span>
            </el-menu-item>
            <el-menu-item index="/market">
              <el-icon><TrendCharts /></el-icon>
              <span>市场数据</span>
            </el-menu-item>
            <el-menu-item index="/analysis">
              <el-icon><DataAnalysis /></el-icon>
              <span>分析与预测</span>
            </el-menu-item>
            <el-menu-item index="/news">
              <el-icon><Reading /></el-icon>
              <span>市场资讯</span>
            </el-menu-item>
            <el-menu-item index="/monitor">
              <el-icon><Monitor /></el-icon>
              <span>系统监控</span>
            </el-menu-item>
            <el-menu-item index="/feedback">
              <el-icon><ChatDotRound /></el-icon>
              <span>意见反馈</span>
            </el-menu-item>
          </el-menu>
        </div>
        <div class="right">
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-dropdown">
              <el-avatar :size="32" :icon="UserFilled" class="user-avatar" />
              <span class="username">{{ store.user?.username || '用户' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="settings" :icon="Setting">系统设置</el-dropdown-item>
                <el-dropdown-item command="change_password" :icon="Lock">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout" :icon="SwitchButton">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
    <router-view v-else />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store'
import { 
  ArrowDown, 
  UserFilled, 
  Setting, 
  Lock, 
  SwitchButton,
  Odometer,
  TrendCharts,
  DataAnalysis,
  Reading,
  Monitor,
  ChatDotRound
} from '@element-plus/icons-vue'
import logoUrl from '@/assets/logo.svg'

const router = useRouter()
const route = useRoute()
const store = useUserStore()
const isAuthed = computed(() => !!store.token)
const activePath = computed(() => route.path)

onMounted(() => {
  if (store.token && !store.user) {
    store.fetchUser()
  }
})

const handleCommand = (command: string) => {
  if (command === 'logout') {
    store.clearToken()
    router.push('/login')
  } else if (command === 'settings') {
    router.push('/settings')
  } else if (command === 'change_password') {
    router.push('/change-password')
  }
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: var(--bg-color-base);
}
#app {
  width: 100%;
  height: 100vh;
}
</style>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: var(--color-header-bg);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  height: 64px;
}

.left {
  display: flex;
  align-items: center;
  height: 100%;
  flex: 1;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 24px;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}

.logo-icon {
  width: 32px;
  height: 32px;
  /* color: #faad14; removed as it is an img */
}

.nav-menu {
  border-bottom: none;
  height: 64px;
  flex: 1;
  min-width: 0;
}

:deep(.el-menu--horizontal > .el-menu-item) {
  height: 64px;
  line-height: 64px;
  border-bottom: none;
}

:deep(.el-menu--horizontal > .el-menu-item.is-active) {
  background-color: var(--el-color-primary) !important;
  border-bottom: none;
}

.right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  background-color: var(--el-color-primary);
}

.username {
  font-size: 14px;
}

.app-main {
  background-color: var(--bg-color-base);
  padding: 24px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
