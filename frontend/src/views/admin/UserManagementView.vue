<template>
  <div>
    <a-page-header title="用户管理">
      <template #extra>
        <a-upload
          :show-upload-list="false"
          :before-upload="handleBeforeUpload"
          accept=".xlsx"
        >
          <a-button :loading="uploading">
            <template #icon><UploadOutlined /></template>
            批量导入用户
          </a-button>
        </a-upload>

        <a-button type="primary" @click="handleAddNew">
          <template #icon><PlusOutlined /></template>
          新增用户
        </a-button>
      </template>
    </a-page-header>

    <div class="content-card">
      <user-table
        :users="users"
        :loading="loading || uploading"
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
import { ref, onMounted, h } from 'vue';
import {
  Button as AButton,
  message,
  Modal,
  PageHeader as APageHeader,
  Upload as AUpload
} from 'ant-design-vue';
import { PlusOutlined, UploadOutlined } from '@ant-design/icons-vue';
import UserTable from '@/components/admin/UserTable.vue';
import UserForm from '@/components/admin/UserForm.vue';
import { userService } from '@/services/userService';
import type { User } from '@/services/types';

// --- 核心修复：在这里定义 users, loading, currentUser 等所有需要的响应式变量 ---
const users = ref<User[]>([]);
const loading = ref(true);
const uploading = ref(false); // 上传状态
const isModalVisible = ref(false);
const currentUser = ref<User | null>(null);
// --- 修复结束 ---

const fetchUsers = async () => {
  loading.value = true;
  try {
    users.value = await userService.getUsers();
  } catch (error) {
    message.error('获取用户列表失败');
  } finally {
    loading.value = false;
  }
};

onMounted(fetchUsers);

const handleAddNew = () => {
  currentUser.value = null;
  isModalVisible.value = true;
};

const handleEdit = (user: User) => {
  currentUser.value = { ...user };
  isModalVisible.value = true;
};

const handleDelete = (userId: number) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除该用户吗？此操作不可恢复。',
    onOk: async () => {
      try {
        await userService.deleteUser(userId);
        message.success('用户删除成功');
        await fetchUsers();
      } catch (error) {
        message.error('删除用户失败');
      }
    },
  });
};

const handleToggleStatus = async (userToToggle: User) => {
  try {
    const updatedUser = await userService.toggleUserStatus(userToToggle.id);
    // 局部更新数据，优化体验
    const index = users.value.findIndex((u: User) => u.id === updatedUser.id);
    if (index !== -1) {
      users.value[index] = updatedUser;
    }
    message.success(`用户状态已更新为 ${updatedUser.is_active ? '启用' : '禁用'}`);
  } catch (error) {
    message.error('更新用户状态失败');
  }
};

const handleBeforeUpload = (file: File) => {
  uploading.value = true;
  userService.batchImportUsers(file)
    .then(result => {
      const { success_count, failure_count, errors } = result;
      const successMessage = `导入完成: ${success_count} 条成功, ${failure_count} 条失败。`;

      if (failure_count > 0) {
        Modal.warning({
          title: successMessage,
          width: 700,
          content: h('div', null, [
            h('p', '以下是导入失败的行和原因:'),
            h('div', { style: { maxHeight: '300px', overflowY: 'auto', marginTop: '10px', background: '#f5f5f5', padding: '10px' } },
              errors.map((e: string) => h('p', { style: { margin: '0 0 5px 0' } }, e))
            ),
          ]),
        });
      } else {
        message.success(successMessage);
      }
      fetchUsers();
    })
    .catch(error => {
      message.error(error.response?.data?.msg || '上传或处理文件时发生严重错误');
    })
    .finally(() => {
      uploading.value = false;
    });

  return false;
};

const handleFormSave = () => {
  isModalVisible.value = false;
  fetchUsers();
};

const handleFormCancel = () => {
  isModalVisible.value = false;
};
</script>

<style scoped>
.content-card {
  background-color: #fff;
  padding: 24px;
  margin: 0 24px;
}
</style>
