// frontend/src/services/orderService.ts

import apiClient from './api'
import type { Order, OrderStatus, WorkLog } from './types'

type OrderCreationData = Partial<Order> & {
  customer_info: object
  requirements_desc: string
}

// --- ADDED: 定义客服可更新的数据类型 ---
type OrderUpdateData = {
  final_price?: number
  developer_id?: number
}

// ---【任务 4.1】新增用于创建工作日志的类型 ---
type WorkLogCreationData = {
  log_content: string
}

export const orderService = {
  getOrders(): Promise<Order[]> {
    return apiClient.get('/orders/').then((res) => res.data)
  },

  createOrder(orderData: OrderCreationData): Promise<Order> {
    return apiClient.post('/orders/', orderData).then((res) => res.data)
  },

  // --- ADDED: 获取单个订单详情 ---
  getOrderById(id: number): Promise<Order> {
    return apiClient.get(`/orders/${id}`).then((res) => res.data)
  },

  // --- ADDED: 更新订单状态 ---
  updateOrderStatus(id: number, status: OrderStatus): Promise<{ message: string }> {
    return apiClient.post(`/orders/${id}/status`, { status }).then((res) => res.data)
  },

  // --- ADDED: 客服更新订单信息 ---
  updateOrderDetails(id: number, data: OrderUpdateData): Promise<Order> {
    return apiClient.patch(`/orders/${id}`, data).then((res) => res.data)
  },
  // ---【任务 4.1】新增调用工作日志API的方法 ---
  addWorkLog(orderId: number, data: WorkLogCreationData): Promise<WorkLog> {
    return apiClient.post(`/orders/${orderId}/work_logs`, data).then((res) => res.data)
  }
}
