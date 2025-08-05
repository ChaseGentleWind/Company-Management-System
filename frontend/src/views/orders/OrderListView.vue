<template>
  <div>
    <a-page-header title="订单管理">
        <template #extra>
         <a-button type="primary" @click="goToCreateOrder">
           <template #icon><PlusOutlined /></template>
           创建新订单
         </a-button>
       </template>
    </a-page-header>

    <div class="content-card">
      <a-table :columns="columns" :data-source="orders" :loading="loading" row-key="id">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">{{ record.status }}</a-tag>
          </template>

          <template v-if="column.key === 'action'">
            <a-space>
              <router-link :to="{ name: 'order-detail', params: { id: record.id } }">
                <a-button type="link" size="small">详情</a-button>
              </router-link>
            </a-space>
          </template>

        </template>
      </a-table>
    </div>
  </div>
</template>

<script setup lang="ts">
// (script 部分基本保持不变, 只需导入 RouterLink)
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router' // 导入 RouterLink
import { message, PageHeader as APageHeader, Button as AButton, Table as ATable, Tag as ATag, Space as ASpace } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { orderService } from '@/services/orderService'
import { type Order, OrderStatus } from '@/services/types'

// ... (其他 script 内容保持不变)
const router = useRouter()
const orders = ref<Order[]>([])
const loading = ref(true)

const columns = [
  { title: '业务ID', dataIndex: 'order_uid', key: 'order_uid' },
  { title: '客户信息', dataIndex: ['customer_info', 'name'], key: 'customer_info', ellipsis: true },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '创建人', dataIndex: ['creator', 'full_name'], key: 'creator' },
  { title: '负责人', dataIndex: ['developer', 'full_name'], key: 'developer' },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action' },
]

const getStatusColor = (status: OrderStatus) => {
  const colorMap: Record<OrderStatus, string> = {
    [OrderStatus.PENDING_ASSIGNMENT]: 'orange',
    [OrderStatus.PENDING_PAYMENT]: 'gold',
    [OrderStatus.IN_DEVELOPMENT]: 'processing',
    [OrderStatus.SHIPPED]: 'blue',
    [OrderStatus.RECEIVED]: 'cyan',
    [OrderStatus.PENDING_SETTLEMENT]: 'purple',
    [OrderStatus.VERIFIED]: 'lime',
    [OrderStatus.SETTLED]: 'success',
    [OrderStatus.CANCELLED]: 'default',
  }
  return colorMap[status] || 'default'
}

const fetchOrders = async () => {
  loading.value = true
  try {
    orders.value = await orderService.getOrders()
  } catch (error) {
    message.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

const goToCreateOrder = () => {
  router.push('/orders/new')
}

onMounted(fetchOrders)
</script>

<style scoped>
.content-card {
  background-color: #fff;
  padding: 24px;
  margin: 0 24px;
}
</style>
