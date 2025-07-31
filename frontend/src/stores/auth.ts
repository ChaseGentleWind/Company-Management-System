import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/services/api'
import router from '@/router'

// 解析JWT Token的函数
function parseJwt(token: string) {
  try {
    return JSON.parse(atob(token.split('.')[1]))
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))
  const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))

  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || null)

  async function login(username: string, password: string): Promise<boolean> {
    try {
      const response = await apiClient.post('/auth/login', { username, password })
      const newTocken = response.data.access_token

      token.value = newTocken
      user.value = parseJwt(newTocken)

      localStorage.setItem('token', newTocken)
      localStorage.setItem('user', JSON.stringify(user.value))

      await router.push('/') // 登录成功后跳转到首页
      return true
    } catch (error) {
      console.error('Login failed:', error)
      // 在这里可以处理登录失败的逻辑，比如显示错误信息
      return false
    }
  }

  function logout() {
    token.value = null
    user.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  return { token, user, isAuthenticated, userRole, login, logout }
})
