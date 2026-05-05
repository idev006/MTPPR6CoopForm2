import api from './api.service'
import type { LoanOrdinaryFormData } from '@/types/form'

export const previewService = {
  async generate(formData: LoanOrdinaryFormData): Promise<void> {
    await api.post('/applications/ordinary/preview', formData)
  },
}
