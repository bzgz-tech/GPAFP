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
            :default-active="activePath"
            background-color="#001529"
            text-color="rgba(255, 255, 255, 0.65)"
            active-text-color="#fff"
            class="nav-menu"
          >
            <el-menu-item index="/">仪表盘</el-menu-item>
            <el-menu-item index="/market">市场数据</el-menu-item>
            <el-menu-item index="/analysis">分析与预测</el-menu-item>
          </el-menu>
        </div>
        <div class="right">
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-dropdown">
              {{ store.user?.username || '用户' }} <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
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
import { ArrowDown } from '@element-plus/icons-vue'
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
  }
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #f0f2f5;
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
  background-color: #001529;
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
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 48px;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}

.logo-icon {
  width: 32px;
  height: 32px;
  color: #faad14;
}

.nav-menu {
  border-bottom: none;
  height: 64px;
  width: 400px;
}

:deep(.el-menu--horizontal > .el-menu-item) {
  height: 64px;
  line-height: 64px;
  border-bottom: none;
}

:deep(.el-menu--horizontal > .el-menu-item.is-active) {
  background-color: #1890ff !important;
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
  gap: 4px;
}

.app-main {
  background-color: #f0f2f5;
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
