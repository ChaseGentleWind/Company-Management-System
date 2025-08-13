// frontend/src/services/userService.ts

import apiClient from './api'
import type { User } from './types'
import type { UserCreationData } from './types'


export const userService = {
  /**
   * 获取所有可访问的用户列表
   */
  getUsers(): Promise<User[]> {
    return apiClient.get('/users/').then((res) => res.data)
  },

  /**
     * 批量导入用户
     * @param file Excel文件对象
     */
  batchImportUsers(file: File): Promise<{ success_count: number; failure_count: number; errors: string[] }> {
      const formData = new FormData();
      formData.append('file', file);

      return apiClient.post('/users/import', formData, {
          headers: {
              'Content-Type': undefined, // 删除Content-Type，让浏览器自动设置multipart/form-data
          },
      }).then(res => res.data);
  },

  /**
   * 【新增】创建新用户
   * @param userData 创建用户所需的数据
   */
  createUser(userData: UserCreationData): Promise<User> {
    return apiClient.post('/users/', userData).then((res) => res.data);
  },

  /**
   * 获取所有已启用的技术人员列表
   */
  getAvailableDevelopers(): Promise<User[]> {
    // 后端GET /users/接口在被客服调用时，会自动只返回技术人员
    return apiClient.get('/users/').then((res) => res.data)
  },

  /**
   * 更新用户信息
   * @param id 用户ID
   * @param userData 要更新的数据
   */
  updateUser(id: number, userData: Partial<User>): Promise<User> {
    return apiClient.put(`/users/${id}`, userData).then((res) => res.data)
  },

  /**
   * 删除用户
   * @param id 用户ID
   */
  deleteUser(id: number): Promise<void> {
    return apiClient.delete(`/users/${id}`).then((res) => res.data)
  },

  /**
   * 切换用户的启用/禁用状态
   * @param id 用户ID
   */
  toggleUserStatus(id: number): Promise<User> {
    return apiClient.patch(`/users/${id}/toggle-status`).then((res) => res.data)
  },
}
