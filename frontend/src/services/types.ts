// frontend/src/services/types.ts

// 定义用户角色的枚举
export enum UserRole {
  SUPER_ADMIN = 'SUPER_ADMIN',
  CUSTOMER_SERVICE = 'CUSTOMER_SERVICE',
  DEVELOPER = 'DEVELOPER',
  FINANCE = 'FINANCE',
}

// 定义用户的接口（数据结构）
export interface User {
  id: number
  username: string
  full_name?: string
  role: UserRole
  gender?: string
  specialized_field?: string
  default_commission_rate?: number
  financial_account?: string
  is_active: boolean
}

// 订单状态枚举
export enum OrderStatus {
  PENDING_ASSIGNMENT = '待匹配',
  PENDING_PAYMENT = '待付款',
  IN_DEVELOPMENT = '开发中',
  SHIPPED = '已发货',
  RECEIVED = '已收货',
  PENDING_SETTLEMENT = '可结算',
  VERIFIED = '已核验',
  SETTLED = '已结算',
  CANCELLED = '已取消',
}

// 用于在订单信息中嵌套显示的用户摘要信息
export interface UserInOrderOut {
  id: number
  username: string
  full_name?: string
}

// 订单数据接口
export interface Order {
  id: number
  customer_info: string
  requirements_desc: string
  initial_budget?: number
  final_price?: number
  status: OrderStatus
  creator_id: number
  developer_id?: number
  special_commission_rate?: number
  created_at: string // 后端传来的是 ISO 格式字符串
  updated_at: string
  shipped_at?: string

  creator: UserInOrderOut
  developer?: UserInOrderOut
}
