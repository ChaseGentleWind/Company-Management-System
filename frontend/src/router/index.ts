// frontend/src/router/index.ts

import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import UserManagementView from '../views/admin/UserManagementView.vue'
// --- 新增导入 ---
import OrderListView from '../views/orders/OrderListView.vue'
import CreateOrderView from '../views/orders/CreateOrderView.vue'

import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // --- home, login, user-management 路由保持不变 ---
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/admin/user-management',
      name: 'user-management',
      component: UserManagementView,
      meta: { requiresAuth: true, requiredRole: 'SUPER_ADMIN' },
    },

    // --- 新增订单相关路由 ---
    {
      path: '/orders',
      name: 'order-list',
      component: OrderListView,
      meta: {
        requiresAuth: true,
        requiredRole: ['CUSTOMER_SERVICE', 'SUPER_ADMIN', 'FINANCE', 'DEVELOPER'],
      }, // 允许多个角色访问
    },
    {
      path: '/orders/new',
      name: 'create-order',
      component: CreateOrderView,
      meta: { requiresAuth: true, requiredRole: 'CUSTOMER_SERVICE' }, // 只有客服能创建
    },
  ],
})

// 全局前置守卫：需要稍微修改以支持多角色判断
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  const targetRequiresAuth = to.meta.requiresAuth
  // 修改为可接受字符串或字符串数组
  const targetRequiredRoles = to.meta.requiredRole as string | string[] | undefined

  if (targetRequiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'home' })
  } else if (targetRequiredRoles) {
    // 如果定义了角色要求
    const userRole = authStore.userRole
    const hasPermission = Array.isArray(targetRequiredRoles)
      ? targetRequiredRoles.includes(userRole)
      : userRole === targetRequiredRoles

    if (!hasPermission) {
      // 角色不匹配，跳转首页或403页面
      next({ name: 'home' })
    } else {
      next()
    }
  } else {
    // 其他情况，正常放行
    next()
  }
})

export default router
