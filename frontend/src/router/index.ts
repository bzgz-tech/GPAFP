import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store'
import Dashboard from '@/pages/Dashboard.vue'
import Login from '@/pages/Login.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: '/market',
    name: 'Market',
    component: () => import('@/pages/Market.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('@/pages/Analysis.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/news',
    name: 'News',
    component: () => import('@/pages/News.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: () => import('@/pages/Monitor.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/pages/Settings.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('@/pages/ChangePassword.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/feedback',
    name: 'Feedback',
    component: () => import('@/pages/Feedback.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/users',
    name: 'UserManagement',
    component: () => import('@/pages/UserManagement.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
