// frontend/src/stores/notifications.ts (新建文件)

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationService } from '@/services/notificationService'
import type { Notification } from '@/services/types'
import { message } from 'ant-design-vue'

export const useNotificationStore = defineStore('notifications', () => {
  const notifications = ref<Notification[]>([])

  const unreadCount = computed(() => {
    return notifications.value.filter((n) => !n.is_read).length
  })

  async function fetchNotifications() {
    try {
      const data = await notificationService.getNotifications()
      notifications.value = data
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
      message.error('获取通知列表失败')
    }
  }

  async function markOneAsRead(notificationId: number) {
    try {
      const updatedNotification = await notificationService.markAsRead(notificationId)
      const index = notifications.value.findIndex((n) => n.id === notificationId)
      if (index !== -1) {
        // --- 核心修复 ---
        // 旧的、存在响应式问题的代码:
        // notifications.value[index] = updatedNotification;

        // 修复后的、能触发响应式更新的代码:
        // 使用 splice 方法替换数组中的元素，以确保 Vue 能够检测到变化
        notifications.value.splice(index, 1, updatedNotification);
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
      message.error('标记已读失败')
    }
  }
  return {
    notifications,
    unreadCount,
    fetchNotifications,
    markOneAsRead,
  }
})
