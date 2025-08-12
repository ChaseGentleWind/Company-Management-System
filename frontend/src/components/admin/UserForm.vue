<template>
  <a-modal
    :open="open"
    :title="isEditMode ? '编辑用户' : '新增用户'"
    @update:open="$emit('update:open', $event)"
    @ok="handleOk"
    :confirm-loading="saving"
  >
    <a-form :model="formState" ref="formRef" layout="vertical" :rules="rules">
      <a-form-item label="用户名" name="username">
        <a-input v-model:value="formState.username" />
      </a-form-item>
      <a-form-item label="姓名" name="full_name">
        <a-input v-model:value="formState.full_name" />
      </a-form-item>
      <a-form-item label="密码" :name="isEditMode ? 'password_optional' : 'password'">
        <a-input-password
          v-model:value="formState.password"
          :placeholder="isEditMode ? '留空则不修改密码' : ''"
        />
      </a-form-item>
      <a-form-item label="角色" name="role">
        <a-select v-model:value="formState.role" :options="roleOptions" />
      </a-form-item>

      <a-form-item label="默认提成比例 (%)" name="default_commission_rate">
        <a-input-number
          v-model:value="formState.default_commission_rate"
          :min="0"
          :max="100"
          :step="0.1"
          placeholder="请输入该用户的默认提成百分比, 如 10.5"
          style="width: 100%"
        />
      </a-form-item>
      <a-form-item label="擅长领域 (技术角色)" name="skills">
        <a-select
          v-model:value="formState.skills"
          mode="tags"
          style="width: 100%"
          placeholder="输入技能后按回车确认, 如 Java, UI设计"
        />
      </a-form-item>

      <a-form-item label="财务账号" name="financial_account">
        <a-input v-model:value="formState.financial_account" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue';
import {
  Modal as AModal,
  Form as AForm,
  FormItem as AFormItem,
  Input as AInput,
  InputPassword as AInputPassword,
  Select as ASelect,
  InputNumber as AInputNumber, // 导入 InputNumber 组件
  message,
} from 'ant-design-vue';
import type { FormInstance, FormProps } from 'ant-design-vue';
import { userService } from '@/services/userService';
import { UserRole, type User, type UserCreationData } from '@/services/types';

const props = defineProps<{
  open: boolean
  user: User | null
}>()

const emit = defineEmits(['save', 'update:open'])

const formRef = ref<FormInstance>()
const formState = reactive<Partial<User & { password?: string }>>({})
const saving = ref(false)

const isEditMode = computed(() => !!props.user?.id)

const rules: FormProps['rules'] = {
  username: [{ required: true, message: '请输入用户名' }],
  role: [{ required: true, message: '请选择角色' }],
  password: [{ required: !isEditMode.value, message: '请输入密码', min: 6 }],
  password_optional: [{ required: false, min: 6, message: '密码至少为6位' }],
}

const roleOptions = Object.values(UserRole).map((role) => ({
  value: role,
  label: role,
}))

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      if (props.user) {
        Object.assign(formState, props.user)
        delete formState.password
      } else {
        Object.keys(formState).forEach((key) => delete (formState as any)[key])
        formState.role = UserRole.DEVELOPER
        formState.skills = []
        // 初始化默认提成为 null 或 undefined，以便 placeholder 生效
        formState.default_commission_rate = undefined;
      }
    } else {
      formRef.value?.resetFields()
    }
  },
)

const handleOk = async () => {
  try {
    await formRef.value?.validate()
    saving.value = true

    // 在提交前，如果提成字段为空字符串，将其转换为 null，以避免后端校验错误
    const payload = { ...formState };
    if (payload.default_commission_rate === null || payload.default_commission_rate === undefined) {
      delete payload.default_commission_rate;
    }

    if (isEditMode.value && props.user) {
      if (!payload.password) {
        delete payload.password
      }
      await userService.updateUser(props.user.id, payload)
      message.success('用户更新成功')
    } else {
      await userService.createUser(payload as UserCreationData);
      message.success('用户创建成功')
    }
    emit('save')
  } catch (error: any) {
    const errorMsg = error.response?.data?.msg || (isEditMode.value ? '更新失败' : '创建失败')
    message.error(errorMsg)
    console.error(error)
  } finally {
    saving.value = false
  }
}
</script>
