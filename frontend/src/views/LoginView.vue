<template>
  <a-layout class="layout-container">
    <a-layout-content class="content-container">
      <a-card title="内部订单管理系统登录" class="login-card">
        <a-form :model="formState" @finish="handleLogin" layout="vertical">
          <a-form-item
            label="用户名"
            name="username"
            :rules="[{ required: true, message: '请输入用户名!' }]"
          >
            <a-input v-model:value="formState.username" />
          </a-form-item>

          <a-form-item
            label="密码"
            name="password"
            :rules="[{ required: true, message: '请输入密码!' }]"
          >
            <a-input-password v-model:value="formState.password" />
          </a-form-item>

          <a-form-item v-if="errorMsg">
            <a-alert :message="errorMsg" type="error" show-icon />
          </a-form-item>

          <a-form-item>
            <a-button type="primary" html-type="submit" :loading="loading" block> 登 录 </a-button>
          </a-form-item>
        </a-form>
      </a-card>
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const formState = reactive({
  username: '',
  password: '',
})

const authStore = useAuthStore()
const loading = ref(false)
const errorMsg = ref('')

const handleLogin = async () => {
  loading.value = true
  errorMsg.value = ''
  const success = await authStore.login(formState.username, formState.password)
  if (!success) {
    errorMsg.value = '用户名或密码错误，请重试。'
  }
  loading.value = false
}
</script>

<style scoped>
.layout-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}
.login-card {
  width: 400px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
</style>
