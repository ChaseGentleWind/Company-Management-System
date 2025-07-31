<template>
  <div class="page-container">
    <a-page-header title="创建新订单" @back="() => $router.go(-1)" />
    <a-card>
      <a-form
        :model="formState"
        ref="formRef"
        layout="vertical"
        :rules="rules"
        @finish="handleFinish"
      >
        <a-form-item label="客户信息" name="customer_info">
          <a-textarea
            v-model:value="formState.customer_info"
            placeholder="请输入客户联系方式、称呼等"
            :rows="4"
          />
        </a-form-item>

        <a-form-item label="需求描述" name="requirements_desc">
          <a-textarea
            v-model:value="formState.requirements_desc"
            placeholder="请详细描述客户的需求"
            :rows="8"
          />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="初始预算 (元)" name="initial_budget">
              <a-input-number v-model:value="formState.initial_budget" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="分配技术" name="developer_id">
              <a-select
                v-model:value="formState.developer_id"
                placeholder="可稍后分配"
                :loading="devsLoading"
                allow-clear
              >
                <a-select-option v-for="dev in developers" :key="dev.id" :value="dev.id">
                  {{ dev.full_name || dev.username }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item>
          <a-space>
            <a-button type="primary" html-type="submit" :loading="submitting"> 提交创建 </a-button>
            <a-button @click="() => $router.go(-1)">取消</a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import type { FormInstance, FormProps } from 'ant-design-vue'
import { userService } from '@/services/userService'
import { orderService } from '@/services/orderService'
import { type User, UserRole } from '@/services/types'

const router = useRouter()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const devsLoading = ref(true)
const developers = ref<User[]>([])

const formState = reactive({
  customer_info: '',
  requirements_desc: '',
  initial_budget: undefined,
  developer_id: undefined,
})

const rules: FormProps['rules'] = {
  customer_info: [{ required: true, message: '请输入客户信息' }],
  requirements_desc: [{ required: true, message: '请输入需求描述' }],
}

// 组件加载时，获取所有技术人员列表用于下拉选择
onMounted(async () => {
  try {
    const allUsers = await userService.getUsers()
    developers.value = allUsers.filter((user) => user.role === UserRole.DEVELOPER && user.is_active)
  } catch (error) {
    message.error('加载技术人员列表失败')
  } finally {
    devsLoading.value = false
  }
})

// 表单提交处理
const handleFinish = async (values: typeof formState) => {
  submitting.value = true
  try {
    await orderService.createOrder(values)
    message.success('订单创建成功！')
    router.push('/orders')
  } catch (error: any) {
    const errorMsg = error.response?.data?.msg || '订单创建失败'
    message.error(errorMsg)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page-container {
  padding: 24px;
}
</style>
