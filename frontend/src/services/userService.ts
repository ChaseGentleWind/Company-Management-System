// frontend/src/services/userService.ts

import apiClient from './api'
// 从我们新建的 types.ts 文件中导入类型，不再在当前文件里定义
import type { User } from './types'

// 我们将创建一个类型文件 - 这句注释可以删掉了

// UserRole 枚举的定义已移至 types.ts - 这里不再需要

// User 接口的定义已移至 types.ts - 这里不再需要

// userService 的实现保持不变
export const userService = {
  getUsers(): Promise<User[]> {
    return apiClient.get('/users/').then((res) => res.data)
  },

  // Partial<User> 表示 userData 对象可以只包含 User 接口中的部分字段
  createUser(userData: Partial<User>): Promise<User> {
    return apiClient.post('/users/', userData).then((res) => res.data)
  },

  updateUser(id: number, userData: Partial<User>): Promise<User> {
    return apiClient.put(`/users/${id}`, userData).then((res) => res.data)
  },

  deleteUser(id: number): Promise<void> {
    return apiClient.delete(`/users/${id}`).then((res) => res.data)
  },

  toggleUserStatus(id: number): Promise<User> {
    return apiClient.patch(`/users/${id}/toggle-status`).then((res) => res.data)
  },
}
