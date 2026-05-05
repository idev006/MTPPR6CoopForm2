import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { authService } from '@/services/auth.service'

export function useAuth() {
  const auth = useAuthStore()
  const router = useRouter()
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function login(email: string, password: string) {
    loading.value = true
    error.value = null
    try {
      const data = await authService.login({ email, password })
      auth.setAuth(data.access_token, data.user)
      const redirect = router.currentRoute.value.query.redirect as string | undefined
      await router.push(redirect || (data.user.role === 'staff' ? '/staff' : '/'))
    } catch (e: unknown) {
      const axiosErr = e as { response?: { data?: { detail?: string } } }
      error.value = axiosErr.response?.data?.detail ?? 'เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่'
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await authService.logout()
    } finally {
      auth.clearAuth()
      await router.push('/login')
    }
  }

  return { login, logout, loading, error }
}
