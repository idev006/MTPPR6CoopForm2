import api from './api.service'
import type { MemberProfile, MemberProfileUpdate } from '@/types/member'

export const memberService = {
  async getProfile(): Promise<MemberProfile> {
    const res = await api.get<MemberProfile>('/members/me/profile')
    return res.data
  },

  async updateProfile(data: MemberProfileUpdate): Promise<MemberProfile> {
    const res = await api.put<MemberProfile>('/members/me/profile', data)
    return res.data
  },
}
