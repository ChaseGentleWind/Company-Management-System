<template>
  <a-modal
    :visible="visible"
    :title="isEditMode ? '编辑用户' : '新增用户'"
    @cancel="$emit('cancel')"
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
      <a-form-item label="擅长领域 (技术角色)" name="specialized_field">
        <a-input v-model:value="formState.specialized_field" />
      </a-form-item>
      <a-form-item label="财务账号" name="financial_account">
        <a-input v-model:value="formState.financial_account" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import {
  Modal as AModal,
  Form as AForm,
  FormItem as AFormItem,
  Input as AInput,
  InputPassword as AInputPassword,
  Select as ASelect,
  message,
} from 'ant-design-vue'
import type { FormInstance, FormProps } from 'ant-design-vue'
import { userService } from '@/services/userService'
import { UserRole, type User } from '@/services/types'

const props = defineProps<{
  visible: boolean
  user: User | null
}>()

const emit = defineEmits(['save', 'cancel'])

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
  () => props.visible,
  (isVisible) => {
    if (isVisible) {
      if (props.user) {
        // 编辑模式
        Object.assign(formState, props.user)
        delete formState.password // 编辑时清空密码字段
      } else {
        // 新增模式
        Object.keys(formState).forEach((key) => delete (formState as any)[key])
        formState.role = UserRole.DEVELOPER // 默认角色
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

    // 移除空的 password 字段，避免后端接收到 ""
    const payload = { ...formState }
    if (!payload.password) {
      delete payload.password
    }

    if (isEditMode.value && props.user) {
      await userService.updateUser(props.user.id, payload)
      message.success('用户更新成功')
    } else {
      await userService.createUser(payload)
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
