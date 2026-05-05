import api from './api.service'
import type { User } from '@/types/user'

export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export const authService = {
  async login(data: LoginRequest): Promise<TokenResponse> {
    const res = await api.post<TokenResponse>('/auth/login', data)
    return res.data
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout')
  },

  async getMe(): Promise<User> {
    const res = await api.get<User>('/auth/me')
    return res.data
  },
}
