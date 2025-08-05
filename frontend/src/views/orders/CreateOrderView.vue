<template>
  <div class="page-container">
    <a-page-header title="创建新订单" @back="() => router.back()" />
    <a-card>
      <a-form
        :model="formState"
        ref="formRef"
        layout="vertical"
        :rules="rules"
        @finish="handleFinish"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="客户姓名" name="customer_name">
              <a-input
                v-model:value="formState.customer_name"
                placeholder="请输入客户的姓名或称呼"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="联系方式" name="customer_phone">
              <a-input
                v-model:value="formState.customer_phone"
                placeholder="请输入客户的电话或其它联系方式"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="需求描述" name="requirements_desc">
          <a-textarea
            v-model:value="formState.requirements_desc"
            placeholder="请详细描述客户的需求"
            :rows="8"
          />
        </a-form-item>

        <a-form-item>
          <a-space>
            <a-button type="primary" html-type="submit" :loading="submitting"> 提交创建 </a-button>
            <a-button @click="() => router.back()">取消</a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import {
  message,
  PageHeader as APageHeader,
  Card as ACard,
  Form as AForm,
  FormItem as AFormItem,
  Input as AInput,
  Textarea as ATextarea,
  Row as ARow,
  Col as ACol,
  Button as AButton,
  Space as ASpace
} from 'ant-design-vue'
import type { FormInstance, FormProps } from 'ant-design-vue'
import { orderService } from '@/services/orderService'

const router = useRouter()
const formRef = ref<FormInstance>()
const submitting = ref(false)

// 表单数据结构，对应UI输入
const formState = reactive({
  customer_name: '',
  customer_phone: '',
  requirements_desc: ''
})

// 表单校验规则
const rules: FormProps['rules'] = {
  customer_name: [{ required: true, message: '请输入客户姓名' }],
  customer_phone: [{ required: true, message: '请输入客户联系方式' }],
  requirements_desc: [{ required: true, message: '请输入需求描述' }]
}

// 表单提交处理
const handleFinish = async () => {
  submitting.value = true
  try {
    // 根据表单数据构建符合后端API要求的payload
    const payload = {
      customer_info: {
        name: formState.customer_name,
        phone: formState.customer_phone
      },
      requirements_desc: formState.requirements_desc
    }
    await orderService.createOrder(payload)
    message.success('订单创建成功！')
    router.push('/orders') // 成功后跳转回订单列表
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
