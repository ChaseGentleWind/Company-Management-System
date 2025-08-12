// frontend/src/router/index.ts

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { UserRole } from '@/services/types'
import { useAuthStore } from '@/stores/auth'
// 引入新布局组件
import MainLayout from '@/layouts/MainLayout.vue'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import UserManagementView from '../views/admin/UserManagementView.vue'
import OrderListView from '../views/orders/OrderListView.vue'
import CreateOrderView from '../views/orders/CreateOrderView.vue'
import OrderDetailView from '../views/orders/OrderDetailView.vue'
import FinanceReportView from '../views/finance/FinanceReportView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    // 主布局路由
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    redirect: '/home', // 默认重定向到首页
    children: [
      {
        path: '/home', // 使用 /home 而不是 /
        name: 'home',
        component: HomeView,
        meta: { title: '首页仪表盘' }
      },
      {
        path: '/admin/user-management',
        name: 'user-management',
        component: UserManagementView,
        meta: { requiredRole: UserRole.SUPER_ADMIN, title: '用户管理' }
      },
      {
        path: '/orders',
        name: 'order-list',
        component: OrderListView,
        meta: {
          requiredRole: [UserRole.CUSTOMER_SERVICE, UserRole.SUPER_ADMIN, UserRole.FINANCE, UserRole.DEVELOPER],
          title: '订单列表'
        }
      },
      {
        path: '/orders/new',
        name: 'create-order',
        component: CreateOrderView,
        meta: { requiredRole: UserRole.CUSTOMER_SERVICE, title: '创建订单' }
      },
      {
        path: '/orders/:id',
        name: 'order-detail',
        component: OrderDetailView,
        props: true,
        meta: {
          requiredRole: [UserRole.CUSTOMER_SERVICE, UserRole.SUPER_ADMIN, UserRole.FINANCE, UserRole.DEVELOPER],
          title: '订单详情'
        }
      },
      {
        path: '/finance/reports',
        name: 'finance-reports',
        component: FinanceReportView,
        meta: { requiredRole: [UserRole.FINANCE, UserRole.SUPER_ADMIN], title: '财务报表' }
      }
    ]
  },
  // 可以在这里添加一个404页面
  // { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFoundView }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 全局前置守卫 (逻辑保持不变, 但现在更强大了)
router.beforeEach((to, from, next) => {
  // --- 添加的调试代码开始 ---
  console.log(
    `%c[ROUTER beforeEach] Navigation
    %cFrom: ${from.fullPath}
    %cTo:   ${to.fullPath}`,
    'color: blue; font-weight: bold;',
    'color: grey;',
    'color: green;'
  )
  // --- 添加的调试代码结束 ---
  const authStore = useAuthStore()

  const targetRequiresAuth = to.matched.some(record => record.meta.requiresAuth);
  // 获取最内层路由的角色要求
  const targetRequiredRoles = to.meta.requiredRole as string | string[] | undefined

  if (targetRequiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'home' })
  } else if (targetRequiredRoles) {
    const userRole = authStore.userRole
    const hasPermission = Array.isArray(targetRequiredRoles)
      ? targetRequiredRoles.includes(userRole)
      : userRole === targetRequiredRoles

    if (!hasPermission) {
      // 可以跳转到无权限页面或首页
      next({ name: 'home' })
    } else {
      next()
    }
  } else {
    next()
  }
})

// --- 添加的调试代码开始 ---
// 全局后置钩子，用于确认导航是否成功
router.afterEach((to, from, failure) => {
  if (failure) {
    console.error(`%c[ROUTER afterEach] FAILED navigation to ${to.fullPath}`, 'color: red; font-weight: bold;', failure)
  } else {
    console.log(`%c[ROUTER afterEach] Navigation to ${to.fullPath} was successful.`, 'color: blue; font-weight: bold;')
  }
})
// --- 添加的调试代码结束 ---

export default router
