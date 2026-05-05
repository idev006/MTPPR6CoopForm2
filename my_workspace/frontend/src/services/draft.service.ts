import api from './api.service'
import type { DraftSession, DraftUpdate } from '@/types/draft'

export const draftService = {
  async createOrGet(form_type: string): Promise<DraftSession> {
    const res = await api.post<DraftSession>('/drafts', { form_type })
    return res.data
  },

  async getByFormType(form_type: string): Promise<DraftSession | null> {
    try {
      const res = await api.get<DraftSession>(`/drafts/${form_type}`)
      return res.data
    } catch (e: unknown) {
      if ((e as { response?: { status?: number } }).response?.status === 404) return null
      throw e
    }
  },

  async update(draft_id: string, data: DraftUpdate): Promise<DraftSession> {
    const res = await api.put<DraftSession>(`/drafts/${draft_id}`, data)
    return res.data
  },

  async delete(draft_id: string): Promise<void> {
    await api.delete(`/drafts/${draft_id}`)
  },
}
