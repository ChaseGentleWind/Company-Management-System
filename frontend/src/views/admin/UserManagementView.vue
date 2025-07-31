<template>
  <div>
    <a-page-header title="用户管理">
      <template #extra>
        <a-button type="primary" @click="handleAddNew">
          <template #icon><PlusOutlined /></template>
          新增用户
        </a-button>
      </template>
    </a-page-header>

    <div class="content-card">
        <user-table
          :users="users"
          :loading="loading"
          @edit="handleEdit"
          @delete="handleDelete"
          @toggle-status="handleToggleStatus"
        />
    </div>

    <user-form
      :visible="isModalVisible"
      :user="currentUser"
      @save="handleFormSave"
      @cancel="handleFormCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Button as AButton, message, Modal, PageHeader as APageHeader } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import UserTable from '@/components/admin/UserTable.vue'
import UserForm from '@/components/admin/UserForm.vue'
import { userService } from '@/services/userService'
import type { User } from '@/services/types'

const users = ref<User[]>([])
const loading = ref(true)
const isModalVisible = ref(false)
const currentUser = ref<User | null>(null)

const fetchUsers = async () => {
  loading.value = true
  try {
    users.value = await userService.getUsers()
  } catch (error) {
    message.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchUsers)

const handleAddNew = () => {
  currentUser.value = null
  isModalVisible.value = true
}

const handleEdit = (user: User) => {
  currentUser.value = { ...user } // 传递副本以避免直接修改表格数据
  isModalVisible.value = true
}

const handleDelete = (userId: number) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除该用户吗？此操作不可恢复。',
    onOk: async () => {
      try {
        await userService.deleteUser(userId)
        message.success('用户删除成功')
        await fetchUsers() // 重新加载数据
      } catch (error) {
        message.error('删除用户失败')
      }
    },
  })
}

const handleToggleStatus = async (userToToggle: User) => {
  try {
    const updatedUser = await userService.toggleUserStatus(userToToggle.id)
    // 局部更新数据，避免重新请求整个列表，优化体验
    const index = users.value.findIndex((u) => u.id === updatedUser.id)
    if (index !== -1) {
      users.value[index] = updatedUser
    }
    message.success(`用户状态已更新为 ${updatedUser.is_active ? '启用' : '禁用'}`)
  } catch (error) {
    message.error('更新用户状态失败')
  }
}

const handleFormSave = () => {
  isModalVisible.value = false
  fetchUsers() // 成功保存后刷新列表
}

const handleFormCancel = () => {
  isModalVisible.value = false
}
</script>

<style scoped>
.content-card {
  background-color: #fff;
  padding: 24px;
  margin: 0 24px;
}
</style>
