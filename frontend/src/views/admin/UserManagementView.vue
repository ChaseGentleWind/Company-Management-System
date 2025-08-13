<template>
  <div>
    <a-card title="用户列表">
      <template #extra>
        <a-space>
          <a-upload :show-upload-list="false" :before-upload="handleBeforeUpload" accept=".xlsx">
            <a-button :loading="uploading">
              <template #icon><UploadOutlined /></template>
              批量导入
            </a-button>
          </a-upload>
          <a-button type="primary" @click="handleAddNew">
            <template #icon><PlusOutlined /></template>
            新增用户
          </a-button>
        </a-space>
      </template>

      <user-table
        :users="users"
        :loading="loading || uploading"
        @edit="handleEdit"
        @delete="handleDelete"
        @toggle-status="handleToggleStatus"
      />
    </a-card>

    <user-form v-model:open="isModalVisible" :user="currentUser" @save="handleFormSave" />

    <import-result-modal
      v-if="importResult.errors.length > 0"
      v-model:open="isResultModalVisible"
      :result="importResult"
    />

    <a-modal
      v-model:open="isDeleteConfirmVisible"
      title="确认删除"
      @ok="confirmDelete"
      :confirm-loading="deleting"
      ok-text="确认"
      cancel-text="取消"
    >
      <p>确定要删除该用户吗？此操作不可恢复。</p>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import {
  Button as AButton,
  message,
  Modal as AModal,
  Card as ACard,
  Upload as AUpload,
  Space as ASpace
} from 'ant-design-vue';
import { PlusOutlined, UploadOutlined } from '@ant-design/icons-vue';
import UserTable from '@/components/admin/UserTable.vue';
import UserForm from '@/components/admin/UserForm.vue';
import ImportResultModal from '@/components/admin/ImportResultModal.vue';
import { userService } from '@/services/userService';
import type { User } from '@/services/types';

// 基础状态
const users = ref<User[]>([]);
const loading = ref(true);
const uploading = ref(false);
const deleting = ref(false);

// 用户表单模态框状态
const isModalVisible = ref(false);
const currentUser = ref<User | null>(null);

// 导入结果模态框状态
const isResultModalVisible = ref(false);
const importResult = reactive({
  title: '',
  errors: [] as string[]
});

// 删除确认模态框状态
const isDeleteConfirmVisible = ref(false);
const userToDeleteId = ref<number | null>(null);

// 获取用户列表
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

// 组件挂载时执行
onMounted(fetchUsers);

// 打开新增用户模态框
const handleAddNew = () => {
  currentUser.value = null;
  isModalVisible.value = true;
};

// 打开编辑用户模态框
const handleEdit = (user: User) => {
  currentUser.value = { ...user };
  isModalVisible.value = true;
};

// 处理删除用户：仅打开确认框并记录ID
const handleDelete = (userId: number) => {
  userToDeleteId.value = userId;
  isDeleteConfirmVisible.value = true;
};

// 当用户在确认框中点击“确定”时，执行此函数
const confirmDelete = async () => {
  if (userToDeleteId.value === null) return;

  deleting.value = true;
  try {
    await userService.deleteUser(userToDeleteId.value);
    message.success('用户删除成功');
    await fetchUsers();
  } catch (error) {
    message.error('删除用户失败');
  } finally {
    // 关闭模态框并重置状态
    isDeleteConfirmVisible.value = false;
    userToDeleteId.value = null;
    deleting.value = false;
  }
};

// 处理切换用户状态
const handleToggleStatus = async (userToToggle: User) => {
  try {
    const updatedUser = await userService.toggleUserStatus(userToToggle.id);
    const index = users.value.findIndex((u: User) => u.id === updatedUser.id);
    if (index !== -1) {
      users.value[index] = updatedUser;
    }
    message.success(`用户状态已更新为 ${updatedUser.is_active ? '启用' : '禁用'}`);
  } catch (error) {
    message.error('更新用户状态失败');
  }
};

// 处理文件上传
const handleBeforeUpload = (file: File) => {
  uploading.value = true;
  userService
    .batchImportUsers(file)
    .then((result) => {
      const { success_count, failure_count, errors } = result;
      const successMessage = `导入完成: ${success_count} 条成功, ${failure_count} 条失败。`;

      if (failure_count > 0) {
        importResult.title = successMessage;
        importResult.errors = errors;
        isResultModalVisible.value = true;
      } else {
        message.success(successMessage);
      }
      fetchUsers();
    })
    .catch((error) => {
      message.error(error.response?.data?.msg || '上传或处理文件时发生严重错误');
    })
    .finally(() => {
      uploading.value = false;
    });
  return false; // 阻止 antd-vue 的默认上传行为
};

// 用户表单保存成功后的回调
const handleFormSave = () => {
  isModalVisible.value = false;
  fetchUsers();
};
</script>
