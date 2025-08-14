import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const apiClient = axios.create({
  // 支持环境变量配置，开发环境使用localhost，生产环境使用相对路径
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：在每个请求前都附加上Token
apiClient.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  const token = authStore.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// --- 响应拦截器 (新增代码) ---
// 在收到响应后进行处理
apiClient.interceptors.response.use(
  // 对于成功的响应 (2xx 状态码)，直接返回
  (response) => response,

  // 对于失败的响应 (非 2xx 状态码)，进行处理
  (error) => {
    // 检查是否是 401 Unauthorized 错误
    if (error.response && error.response.status === 401) {
      // 如果是 401 错误，说明 token 无效或已过期
      const authStore = useAuthStore()
      console.error('Authentication Error: Token is invalid or expired. Logging out.')
      // 调用 logout 方法，它会清空本地存储并跳转到登录页
      authStore.logout()
    }
    // 将错误继续抛出，以便组件中的 .catch() 可以捕获到
    return Promise.reject(error)
  }
)

export default apiClient
