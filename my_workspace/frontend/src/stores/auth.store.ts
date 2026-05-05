import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/user'
import { ROLE_LABELS, type UserRole } from '@/constants/roles'

export const useAuthStore = defineStore('auth', () => {
  // access token เก็บใน memory เท่านั้น (ไม่เก็บ localStorage)
  const accessToken = ref<string | null>(null)
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value)

  const roleLabel = computed(() => {
    if (!user.value) return ''
    return ROLE_LABELS[user.value.role as UserRole] || user.value.role
  })

  function hasRole(allowedRoles: string[] | string) {
    if (!user.value) return false
    const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles]
    return roles.includes(user.value.role)
  }

  function setAuth(token: string, userData: User) {
    accessToken.value = token
    user.value = userData
  }

  function clearAuth() {
    accessToken.value = null
    user.value = null
  }

  return { accessToken, user, isAuthenticated, roleLabel, hasRole, setAuth, clearAuth }
})
