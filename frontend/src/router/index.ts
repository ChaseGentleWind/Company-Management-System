// frontend/src/router/index.ts (Corrected and Complete)

import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import FinanceReportView from '../views/finance/FinanceReportView.vue';
import HomeView from '../views/HomeView.vue'
import UserManagementView from '../views/admin/UserManagementView.vue'
import OrderListView from '../views/orders/OrderListView.vue'
import CreateOrderView from '../views/orders/CreateOrderView.vue'
import OrderDetailView from '../views/orders/OrderDetailView.vue'

import { useAuthStore } from '@/stores/auth'
import { UserRole } from '@/services/types' // 建议导入枚举以提高代码健壮性

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // --- 补全缺失的路由 ---
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true } // 首页需要登录
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/admin/user-management',
      name: 'user-management',
      component: UserManagementView,
      meta: { requiresAuth: true, requiredRole: UserRole.SUPER_ADMIN } // 仅限超管访问
    },
    // --- 已有的订单路由保持不变 ---
    {
      path: '/orders',
      name: 'order-list',
      component: OrderListView,
      meta: {
        requiresAuth: true,
        // 多角色权限
        requiredRole: [
          UserRole.CUSTOMER_SERVICE,
          UserRole.SUPER_ADMIN,
          UserRole.FINANCE,
          UserRole.DEVELOPER
        ]
      }
    },
    {
      path: '/orders/new',
      name: 'create-order',
      component: CreateOrderView,
      meta: { requiresAuth: true, requiredRole: UserRole.CUSTOMER_SERVICE }
    },
    {
        path: '/finance/reports',
        name: 'finance-reports',
        component: FinanceReportView,
        meta: { 
            requiresAuth: true, 
            requiredRole: [UserRole.FINANCE, UserRole.SUPER_ADMIN] 
        }
    },
    {
      path: '/orders/:id',
      name: 'order-detail',
      component: OrderDetailView,
      props: true, // 将路由参数作为props传递给组件
      meta: {
        requiresAuth: true,
        requiredRole: [
          UserRole.CUSTOMER_SERVICE,
          UserRole.SUPER_ADMIN,
          UserRole.FINANCE,
          UserRole.DEVELOPER
        ]
      }
    }
  ]
})

// 全局前置守卫 (这里的逻辑是正确的，无需修改)
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  const targetRequiresAuth = to.meta.requiresAuth
  const targetRequiredRoles = to.meta.requiredRole as string | string[] | undefined

  // 1. 如果目标路由需要认证，但用户未登录
  if (targetRequiresAuth && !authStore.isAuthenticated) {
    // 将用户重定向到登录页
    next({ name: 'login', query: { redirect: to.fullPath } })
  }
  // 2. 如果用户已登录，但尝试访问登录页
  else if (to.name === 'login' && authStore.isAuthenticated) {
    // 将用户重定向到首页
    next({ name: 'home' })
  }
  // 3. 如果目标路由有角色要求
  else if (targetRequiredRoles) {
    const userRole = authStore.userRole
    const hasPermission = Array.isArray(targetRequiredRoles)
      ? targetRequiredRoles.includes(userRole)
      : userRole === targetRequiredRoles

    if (!hasPermission) {
      // 角色不匹配，跳转到首页（或一个专门的403页面）
      next({ name: 'home' })
    } else {
      // 权限OK，放行
      next()
    }
  }
  // 4. 其他所有情况，直接放行
  else {
    next()
  }
})

export default router
