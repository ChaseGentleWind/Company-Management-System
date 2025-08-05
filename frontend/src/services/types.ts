// frontend/src/services/types.ts (Corrected)

// 定义用户角色的枚举
export enum UserRole {
  SUPER_ADMIN = 'SUPER_ADMIN',
  CUSTOMER_SERVICE = 'CUSTOMER_SERVICE',
  DEVELOPER = 'DEVELOPER',
  FINANCE = 'FINANCE'
}

// 定义用户的接口（数据结构）
export interface User {
  id: number
  username: string
  full_name?: string
  role: UserRole
  gender?: string
  skills?: string[] // Changed from specialized_field
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
  CANCELLED = '已取消'
}

// 用于在订单信息中嵌套显示的用户摘要信息
export interface UserInOrderOut {
  id: number
  full_name?: string
}

// 工作日志接口
export interface WorkLog {
  id: number
  log_content: string
  created_at: string
  developer: {
    id: number
    full_name: string | null
  }
}

// 提成记录接口
export interface Commission {
  id: number
  user_id: number
  amount: number
  role_at_time: string
  created_at: string
  full_name?: string
}

// 订单数据接口 - Updated to match backend's OrderOut schema
export interface Order {
  id: number
  order_uid: string
  customer_info: { [key: string]: any } // Changed from string to object
  requirements_desc: string
  final_price?: number
  status: OrderStatus
  creator: UserInOrderOut
  developer?: UserInOrderOut
  commission_rate_override?: { [key: string]: number } | null
  is_locked: boolean // Added missing property
  created_at: string
  updated_at: string
  shipped_at?: string | null
  logs: WorkLog[]
  commissions: Commission[]
}

export interface Notification {
  id: number;
  content: string;
  is_read: boolean;
  related_order_id: number | null;
  created_at: string;
}
