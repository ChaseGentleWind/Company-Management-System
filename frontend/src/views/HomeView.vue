<template>
  <div>
    <a-page-header :title="pageTitle" :sub-title="pageSubTitle" />

    <div v-if="loading" class="loading-container">
      <a-spin size="large" />
    </div>

    <div v-else class="content-grid">
      <template v-if="authStore.userRole === UserRole.SUPER_ADMIN && globalStats">
        <a-row :gutter="[16, 16]">
          <a-col :span="6">
            <a-statistic title="总用户数" :value="globalStats.total_users" class="stat-card" />
          </a-col>
          <a-col :span="6">
            <a-statistic title="总订单数" :value="globalStats.total_orders" class="stat-card" />
          </a-col>
          <a-col :span="12">
            <a-statistic
              title="累计结算总额 (元)"
              :precision="2"
              :value="globalStats.total_settled_value"
              class="stat-card"
            />
          </a-col>
          <a-col :span="24">
            <a-card title="订单状态分布">
              <v-chart class="chart" :option="pieChartOption" autoresize />
            </a-card>
          </a-col>
        </a-row>
      </template>

      <template v-if="isEmployee && personalStats">
        <a-row :gutter="[16, 16]">
          <a-col :span="12">
             <a-statistic
               :title="personalStatTitle"
               :value="personalStats.monthly_orders_created ?? personalStats.monthly_orders_completed ?? 0"
               class="stat-card"
             />
          </a-col>
          <a-col :span="12">
            <a-statistic
              title="累计获得总提成 (元)"
              :precision="2"
              :value="personalStats.total_commission_earned"
              class="stat-card"
            />
          </a-col>
        </a-row>
         <a-alert
          message="提示"
          description="这里展示的是您个人的关键业绩指标。本月数据会在每月初重置。"
          type="info"
          show-icon
          style="margin-top: 24px;"
        />
      </template>

       <template v-if="authStore.userRole === UserRole.FINANCE">
        <a-card>
          <a-empty
            image="https://gw.alipayobjects.com/mdn/miniapp_social/afts/img/A*pevERLJC9v0AAAAAAAAAAABjAQAAAQ/original"
            description="欢迎使用财务功能，请点击顶部导航栏的【财务报表】开始您的工作。"
          />
        </a-card>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { UserRole } from '@/services/types';
import { dashboardService, type GlobalDashboardStats, type PersonalDashboardStats } from '@/services/dashboardService';
import {
  PageHeader as APageHeader,
  Card as ACard,
  Spin as ASpin,
  Statistic as AStatistic,
  Row as ARow,
  Col as ACol,
  Alert as AAlert,
  Empty as AEmpty,
  message
} from 'ant-design-vue';

// 引入 ECharts
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, PieChart, TitleComponent, TooltipComponent, LegendComponent]);

const authStore = useAuthStore();
const loading = ref(true);

const globalStats = ref<GlobalDashboardStats | null>(null);
const personalStats = ref<PersonalDashboardStats | null>(null);

// 动态计算页面标题
const pageTitle = computed(() => {
  switch (authStore.userRole) {
    case UserRole.SUPER_ADMIN: return '全局数据看板';
    case UserRole.CUSTOMER_SERVICE:
    case UserRole.DEVELOPER: return '个人工作台';
    case UserRole.FINANCE: return '财务工作台';
    default: return '首页';
  }
});

const pageSubTitle = computed(() => `欢迎回来, ${authStore.user?.full_name || authStore.user?.username}!`);

const isEmployee = computed(() =>
  authStore.userRole === UserRole.CUSTOMER_SERVICE || authStore.userRole === UserRole.DEVELOPER
);

const personalStatTitle = computed(() => {
    return authStore.userRole === UserRole.CUSTOMER_SERVICE ? '本月创建订单数' : '本月完成订单数'
});

// ECharts 饼图配置
const pieChartOption = computed(() => {
  const data = globalStats.value?.status_distribution
    ? Object.entries(globalStats.value.status_distribution).map(([name, value]) => ({ name, value }))
    : [];

  return {
    tooltip: { trigger: 'item', formatter: '{a} <br/>{b} : {c} ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name) },
    series: [
      {
        name: '订单状态',
        type: 'pie',
        radius: '75%',
        center: ['60%', '50%'],
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  };
});

// 组件挂载时根据角色获取数据
onMounted(async () => {
  loading.value = true;
  try {
    if (authStore.userRole === UserRole.SUPER_ADMIN) {
      globalStats.value = await dashboardService.getGlobalDashboard();
    } else if (isEmployee.value) {
      personalStats.value = await dashboardService.getPersonalDashboard();
    }
  } catch (error) {
    console.error("Failed to fetch dashboard data:", error);
    message.error("数据加载失败！");
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.content-grid {
  padding: 0 24px;
}
.loading-container {
  text-align: center;
  padding: 50px;
}
.stat-card {
  background-color: #fff;
  padding: 24px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.09);
}
.chart {
  height: 400px;
}
</style>
