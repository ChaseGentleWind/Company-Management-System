<template>
  <a-card title="添加工作日志">
    <a-form :model="logFormState" layout="vertical" @finish="handleLogSubmit" ref="formRef">
      <a-form-item label="日志内容" name="log_content" :rules="[{ required: true, message: '日志内容不能为空' }]">
        <a-textarea v-model:value="logFormState.log_content" :rows="4" placeholder="请填写工作进展..." />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" html-type="submit" :loading="isLogSubmitting">提交日志</a-button>
      </a-form-item>
    </a-form>
  </a-card>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { orderService } from '@/services/orderService';
import { message, Card as ACard, Form as AForm, FormItem as AFormItem, Textarea as ATextarea, Button as AButton } from 'ant-design-vue';
import type { FormInstance } from 'ant-design-vue';

const props = defineProps({
  orderId: {
    type: Number,
    required: true
  }
});

const emit = defineEmits(['log-added']);

const formRef = ref<FormInstance>();
const logFormState = reactive({ log_content: '' });
const isLogSubmitting = ref(false);

const handleLogSubmit = async () => {
  isLogSubmitting.value = true;
  try {
    await orderService.addWorkLog(props.orderId, { log_content: logFormState.log_content });
    message.success('工作日志提交成功');
    logFormState.log_content = ''; // 重置表单
    formRef.value?.clearValidate();
    emit('log-added'); // 通知父组件刷新数据
  } catch (error: any) {
    message.error(error.response?.data?.msg || '日志提交失败');
  } finally {
    isLogSubmitting.value = false;
  }
};
</script>
