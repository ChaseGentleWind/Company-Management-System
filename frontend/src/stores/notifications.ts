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
      // 在列表中找到对应的通知并更新其状态，以实现即时响应
      const index = notifications.value.findIndex((n) => n.id === notificationId)
      if (index !== -1) {
        notifications.value[index] = updatedNotification
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
