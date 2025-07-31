// frontend/src/services/orderService.ts

import apiClient from './api'
import type { Order } from './types'

// 用于创建订单的数据类型
// Partial<Order> 意味着我们可以只提供部分字段
type OrderCreationData = Partial<Order> & {
  customer_info: string
  requirements_desc: string
}

export const orderService = {
  /**
   * 获取订单列表 (根据用户角色由后端决定返回哪些)
   */
  getOrders(): Promise<Order[]> {
    return apiClient.get('/orders/').then((res) => res.data)
  },

  /**
   * 创建一个新订单
   * @param orderData 创建订单所需的数据
   */
  createOrder(orderData: OrderCreationData): Promise<Order> {
    return apiClient.post('/orders/', orderData).then((res) => res.data)
  },

  // 后续我们会在这里添加更多函数，如更新状态、分配技术等
}
