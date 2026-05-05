import axios, { type AxiosInstance } from 'axios'
import { useAuthStore } from '@/stores/auth.store'

const api: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,  // ส่ง HttpOnly refresh token cookie ด้วย
  timeout: 30_000,
})

// request interceptor — attach access token
api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

// response interceptor — handle 401 + token refresh
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const res = await axios.post('/api/v1/auth/refresh', {}, { withCredentials: true })
        const auth = useAuthStore()
        auth.setAuth(res.data.access_token, res.data.user)
        original.headers.Authorization = `Bearer ${res.data.access_token}`
        return api(original)
      } catch {
        const auth = useAuthStore()
        auth.clearAuth()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
