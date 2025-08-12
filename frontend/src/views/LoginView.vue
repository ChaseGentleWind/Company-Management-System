<template>
  <div class="login-container">
    <div class="login-box">
      <div class="left-panel">
        <img src="@/assets/logo.svg" alt="logo" class="logo-img"/>
        <h2>公司内部管理系统</h2>
        <p>高效、协同、智能</p>
      </div>
      <div class="right-panel">
        <a-form
          :model="formState"
          @finish="handleLogin"
          layout="vertical"
          class="login-form"
        >
          <h3>欢迎回来！</h3>
          <a-form-item
            label="用户名"
            name="username"
            :rules="[{ required: true, message: '请输入用户名!' }]"
          >
            <a-input v-model:value="formState.username" placeholder="请输入您的账户" size="large">
                <template #prefix><UserOutlined /></template>
            </a-input>
          </a-form-item>

          <a-form-item
            label="密码"
            name="password"
            :rules="[{ required: true, message: '请输入密码!' }]"
          >
            <a-input-password v-model:value="formState.password" placeholder="请输入您的密码" size="large">
                <template #prefix><LockOutlined /></template>
            </a-input-password>
          </a-form-item>

          <a-form-item v-if="errorMsg">
            <a-alert :message="errorMsg" type="error" show-icon />
          </a-form-item>

          <a-form-item>
            <a-button type="primary" html-type="submit" :loading="loading" block size="large">
              登 录
            </a-button>
          </a-form-item>
        </a-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue';

const formState = reactive({
  username: '',
  password: '',
});

const authStore = useAuthStore();
const loading = ref(false);
const errorMsg = ref('');

const handleLogin = async () => {
  loading.value = true;
  errorMsg.value = '';
  const success = await authStore.login(formState.username, formState.password);
  if (!success) {
    errorMsg.value = '用户名或密码错误，请重试。';
  }
  loading.value = false;
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-image: linear-gradient(to top, #f3e7e9 0%, #e3eeff 99%, #e3eeff 100%);
}

.login-box {
  width: 800px;
  height: 500px;
  display: flex;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.left-panel {
  width: 45%;
  background: linear-gradient(135deg, #1677ff, #52c41a);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  text-align: center;
}

.left-panel .logo-img {
    width: 80px;
    height: 80px;
    margin-bottom: 20px;
}

.left-panel h2 {
  color: #fff;
  font-size: 28px;
  margin-bottom: 10px;
}

.left-panel p {
  font-size: 16px;
  opacity: 0.9;
}

.right-panel {
  width: 55%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.login-form {
  width: 100%;
}

.login-form h3 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #333;
}
</style>
