// frontend/src/services/notificationService.ts (新建文件)

import apiClient from './api'
import type { Notification } from './types' // 确保你的 types.ts 文件导出了 Notification 类型

export const notificationService = {
  /**
   * 获取当前用户的所有通知
   */
  getNotifications(): Promise<Notification[]> {
    return apiClient.get('/notifications/').then((res) => res.data)
  },

  /**
   * 将单条通知标记为已读
   * @param notificationId 要标记的通知ID
   */
  markAsRead(notificationId: number): Promise<Notification> {
    return apiClient.post(`/notifications/${notificationId}/read`).then((res) => res.data)
  }
}
