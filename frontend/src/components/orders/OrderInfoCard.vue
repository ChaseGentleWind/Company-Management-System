<template>
  <a-card title="订单信息">
    <a-descriptions v-if="order" bordered :column="2">
      <a-descriptions-item label="业务ID">{{ order.order_uid }}</a-descriptions-item>
      <a-descriptions-item label="订单状态">
        <a-tag :color="getStatusColor(order.status)">{{ order.status }}</a-tag>
      </a-descriptions-item>
      <a-descriptions-item label="客户姓名">{{ order.customer_info.name }}</a-descriptions-item>
      <a-descriptions-item label="联系方式">{{ order.customer_info.phone }}</a-descriptions-item>
      <a-descriptions-item label="最终价格">{{ order.final_price ?? '未定价' }} 元</a-descriptions-item>
      <a-descriptions-item label="创建人(客服)">{{ order.creator.full_name }}</a-descriptions-item>
      <a-descriptions-item label="负责人(技术)">{{ order.developer?.full_name ?? '未分配' }}</a-descriptions-item>
      <a-descriptions-item label="创建时间">{{ new Date(order.created_at).toLocaleString() }}</a-descriptions-item>
      <a-descriptions-item label="需求描述" :span="2">{{ order.requirements_desc }}</a-descriptions-item>
    </a-descriptions>
  </a-card>
</template>

<script setup lang="ts">
import { type PropType } from 'vue'
import { type Order, OrderStatus } from '@/services/types'
import { Card as ACard, Descriptions as ADescriptions, DescriptionsItem as ADescriptionsItem, Tag as ATag } from 'ant-design-vue'

defineProps({
  order: {
    type: Object as PropType<Order | null>,
    required: true
  }
})

const getStatusColor = (status: OrderStatus) => {
  const colorMap: Record<OrderStatus, string> = {
    [OrderStatus.PENDING_ASSIGNMENT]: 'orange',
    [OrderStatus.PENDING_PAYMENT]: 'gold',
    [OrderStatus.PAID]: 'purple',
    [OrderStatus.IN_DEVELOPMENT]: 'processing',
    [OrderStatus.SHIPPED]: 'blue',
    [OrderStatus.RECEIVED]: 'cyan',
    [OrderStatus.PENDING_SETTLEMENT]: 'purple',
    [OrderStatus.VERIFIED]: 'lime',
    [OrderStatus.SETTLED]: 'success',
    [OrderStatus.CANCELLED]: 'default',
  };
  return colorMap[status] || 'default';
};
</script>
