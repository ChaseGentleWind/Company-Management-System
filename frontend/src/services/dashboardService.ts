// frontend/src/services/dashboardService.ts

import apiClient from './api'

// 定义个人仪表盘数据的接口
export interface PersonalDashboardStats {
  monthly_orders_created?: number;
  monthly_orders_completed?: number;
  total_commission_earned: number;
}

// 定义全局仪表盘数据的接口
export interface GlobalDashboardStats {
  total_users: number;
  total_orders: number;
  total_settled_value: number;
  status_distribution: { [key: string]: number };
}

export const dashboardService = {
  /**
   * 获取个人业绩数据 (客服/技术)
   */
  getPersonalDashboard(): Promise<PersonalDashboardStats> {
    return apiClient.get('/v1/dashboard/personal').then((res) => res.data)
  },

  /**
   * 获取全局统计数据 (超管)
   */
  getGlobalDashboard(): Promise<GlobalDashboardStats> {
    return apiClient.get('/v1/dashboard/global').then((res) => res.data)
  }
}
