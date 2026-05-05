import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import router from './router'
import './assets/main.css'

async function bootstrap() {
  const app = createApp(App)
  const pinia = createPinia()
  app.use(pinia)

  // Restore session BEFORE router mounts — so beforeEach sees correct auth state.
  // 401 = no valid cookie, stay logged out (expected on first visit).
  try {
    const { useAuthStore } = await import('./stores/auth.store')
    const auth = useAuthStore()
    const res = await axios.post('/api/v1/auth/refresh', {}, { withCredentials: true })
    auth.setAuth(res.data.access_token, res.data.user)
  } catch {
    // no valid refresh token
  }

  app.use(router)
  app.mount('#app')
}

bootstrap()
