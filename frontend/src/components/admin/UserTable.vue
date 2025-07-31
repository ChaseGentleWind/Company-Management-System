<template>
  <a-table :columns="columns" :data-source="users" :loading="loading" row-key="id">
    <template #bodyCell="{ column, record }">
      <template v-if="column.key === 'role'">
        <a-tag :color="getRoleColor(record.role)">{{ record.role }}</a-tag>
      </template>
      <template v-if="column.key === 'is_active'">
        <a-tag :color="record.is_active ? 'green' : 'red'">
          {{ record.is_active ? '启用' : '禁用' }}
        </a-tag>
      </template>
      <template v-if="column.key === 'action'">
        <a-space>
          <a-button type="link" @click="$emit('edit', record)">编辑</a-button>
          <a-button type="link" @click="$emit('toggle-status', record)">
            {{ record.is_active ? '禁用' : '启用' }}
          </a-button>
          <a-button type="link" danger @click="$emit('delete', record.id)">删除</a-button>
        </a-space>
      </template>
    </template>
  </a-table>
</template>

<script setup lang="ts">
import { Table as ATable, Tag as ATag, Space as ASpace, Button as AButton } from 'ant-design-vue'
import type { User, UserRole } from '@/services/types'

defineProps<{
  users: User[]
  loading: boolean
}>()

defineEmits(['edit', 'delete', 'toggle-status'])

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', sorter: (a: User, b: User) => a.id - b.id },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '姓名', dataIndex: 'full_name', key: 'full_name' },
  { title: '角色', dataIndex: 'role', key: 'role' },
  { title: '状态', dataIndex: 'is_active', key: 'is_active' },
  { title: '操作', key: 'action' },
]

const getRoleColor = (role: UserRole) => {
  const colors: Record<UserRole, string> = {
    SUPER_ADMIN: 'gold',
    CUSTOMER_SERVICE: 'blue',
    DEVELOPER: 'geekblue',
    FINANCE: 'purple',
  }
  return colors[role] || 'default'
}
</script>
