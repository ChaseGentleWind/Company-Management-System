<template>
  <a-drawer
    :visible="visible"
    title="通知中心"
    placement="right"
    @close="$emit('close')"
    :width="400"
  >
    <a-list item-layout="horizontal" :data-source="notificationStore.notifications">
      <template #renderItem="{ item }">
        <a-list-item
          :class="{ 'notification-read': item.is_read }"
          @click="handleItemClick(item)"
        >
          <a-list-item-meta :description="item.content">
            <template #title>
              <a-badge :dot="!item.is_read" status="processing" />
              <span> 订单相关通知</span>
            </template>
          </a-list-item-meta>
          <div class="notification-time">{{ formatTime(item.created_at) }}</div>
        </a-list-item>
      </template>

      <template #header v-if="notificationStore.notifications.length > 0">
        <div style="text-align: right;">
            </div>
      </template>

      <template #loadMore>
        <div v-if="notificationStore.notifications.length === 0" style="text-align: center; margin-top: 20px;">
          <a-empty description="暂无通知" />
        </div>
      </template>
    </a-list>
  </a-drawer>
</template>

<script setup lang="ts">
import {
  Drawer as ADrawer,
  List as AList,
  ListItem as AListItem,
  ListItemMeta as AListItemMeta,
  Badge as ABadge,
  Empty as AEmpty,
} from 'ant-design-vue'
import { useNotificationStore } from '@/stores/notifications'
import { useRouter } from 'vue-router'
import type { Notification } from '@/services/types'

defineProps<{
  visible: boolean
}>()

const emit = defineEmits(['close'])

const notificationStore = useNotificationStore()
const router = useRouter()

const formatTime = (timeStr: string) => {
    // 简单的相对时间格式化
    const seconds = Math.floor((new Date().getTime() - new Date(timeStr).getTime()) / 1000)
    let interval = seconds / 31536000
    if (interval > 1) return Math.floor(interval) + " 年前"
    interval = seconds / 2592000
    if (interval > 1) return Math.floor(interval) + " 个月前"
    interval = seconds / 86400
    if (interval > 1) return Math.floor(interval) + " 天前"
    interval = seconds / 3600
    if (interval > 1) return Math.floor(interval) + " 小时前"
    interval = seconds / 60
    if (interval > 1) return Math.floor(interval) + " 分钟前"
    return "刚刚"
}

const handleItemClick = (item: Notification) => {
    // 如果未读，则标记为已读
    if (!item.is_read) {
        notificationStore.markOneAsRead(item.id)
    }
    // 如果有关联订单，则跳转到订单详情页
    if (item.related_order_id) {
        router.push(`/orders/${item.related_order_id}`)
        emit('close') // 关闭抽屉
    }
}

</script>

<style scoped>
.notification-read {
  color: #888;
  background-color: #f7f7f7;
}
.notification-time {
    font-size: 12px;
    color: #aaa;
    margin-left: 16px;
}
.ant-list-item {
    cursor: pointer;
    transition: background-color 0.3s;
}
.ant-list-item:hover {
    background-color: #e6f7ff;
}
</style>