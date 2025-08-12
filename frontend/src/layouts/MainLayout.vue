<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible theme="dark">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="logo" />
        <h1 v-if="!collapsed">管理系统</h1>
      </div>
      <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline">
        <a-menu-item key="/">
          <router-link to="/">
            <pie-chart-outlined />
            <span>首页</span>
          </router-link>
        </a-menu-item>

        <a-menu-item key="/orders" v-if="allowedOrderRoles.includes(authStore.userRole)">
          <router-link to="/orders">
            <shopping-cart-outlined />
            <span>订单管理</span>
          </router-link>
        </a-menu-item>

        <a-menu-item key="/finance/reports" v-if="['FINANCE', 'SUPER_ADMIN'].includes(authStore.userRole)">
          <router-link to="/finance/reports">
            <line-chart-outlined />
            <span>财务报表</span>
          </router-link>
        </a-menu-item>

        <a-menu-item key="/admin/user-management" v-if="authStore.userRole === 'SUPER_ADMIN'">
          <router-link to="/admin/user-management">
            <team-outlined />
            <span>用户管理</span>
          </router-link>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>

    <a-layout>
      <a-layout-header class="header">
        <div class="header-left">
          <a-breadcrumb>
            <a-breadcrumb-item>
              <router-link to="/">主页</router-link>
            </a-breadcrumb-item>
            <a-breadcrumb-item v-if="$route.meta.title">{{ $route.meta.title }}</a-breadcrumb-item>
          </a-breadcrumb>
        </div>
        <div class="header-right">
          <a-space :size="20">
            <a-badge :count="notificationStore.unreadCount">
              <bell-outlined style="font-size: 18px; cursor: pointer" @click="showDrawer" />
            </a-badge>
            <a-dropdown>
              <a class="ant-dropdown-link" @click.prevent>
                <a-avatar size="small" style="background-color: #1677ff; margin-right: 8px">
                  {{ authStore.user?.full_name?.charAt(0) || 'U' }}
                </a-avatar>
                你好, {{ authStore.user?.full_name || authStore.user?.username }}
                <down-outlined />
              </a>
              <template #overlay>
                <a-menu>
                  <a-menu-item @click="authStore.logout()">
                    <logout-outlined />
                    登出系统
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </a-space>
        </div>
      </a-layout-header>

      <a-layout-content class="content">
      <router-view v-slot="{ Component, route }">
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </a-layout-content>
    </a-layout>
  </a-layout>

  <notification-center :visible="drawerVisible" @close="drawerVisible = false" />
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notifications';
import NotificationCenter from '@/components/NotificationCenter.vue';
import {
  PieChartOutlined,
  ShoppingCartOutlined,
  LineChartOutlined,
  TeamOutlined,
  BellOutlined,
  DownOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue';

const collapsed = ref<boolean>(false);
const route = useRoute();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const allowedOrderRoles = ['SUPER_ADMIN', 'CUSTOMER_SERVICE', 'DEVELOPER', 'FINANCE'];

// 根据路由路径动态计算选中的菜单项
const selectedKeys = computed(() => {
  const path = route.path;
  if (path.startsWith('/orders')) return ['/orders'];
  if (path.startsWith('/admin')) return ['/admin/user-management'];
  if (path.startsWith('/finance')) return ['/finance/reports'];
  return [path];
});


// 通知中心抽屉逻辑
const drawerVisible = ref(false);
const showDrawer = () => {
  notificationStore.fetchNotifications();
  drawerVisible.value = true;
};

// 监听登录状态获取通知
watch(
  () => authStore.isAuthenticated,
  (isAuth) => {
    if (isAuth) {
      notificationStore.fetchNotifications();
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.logo {
  height: 32px;
  margin: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  overflow: hidden;
}

.logo img {
  height: 32px;
  width: 32px;
}

.logo h1 {
  color: white;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
}

.header {
  background: #fff;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.content {
  margin: 24px;
  background: #f0f2f5; /* 这是内容区的背景色 */
  padding: 24px;
  background: #fff; /* 内容区里的 router-view 背景是白色 */
  min-height: 280px;
}

.ant-layout-content {
    background-color: #f0f2f5;
    padding: 24px;
}
.ant-layout-content .router-view-content {
    background: #fff;
    padding: 24px;
    min-height: calc(100vh - 64px - 48px);
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
