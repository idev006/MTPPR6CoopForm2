import api from './api.service'

export interface SubmitResponse {
  success: boolean
  application_no: string
  application_id: string
  message?: string
}

export interface ApplicationListItem {
  id: string
  application_no: string
  form_type: string
  status: string
  created_at: string
}

export interface ApplicationDetail {
  id: string
  application_no: string
  form_type: string
  status: string
  requested_amount: number | null
  requested_installments: number | null
  loan_purpose: string | null
  created_at: string
  submitted_at: string | null
  reviewed_at: string | null
  review_remarks: string | null
  cancelled_at: string | null
  cancel_reason: string | null
  has_pdf: boolean
}

export const applicationService = {
  async submit(data: any, formType = 'loan_ordinary', draftId?: string | null): Promise<SubmitResponse> {
    const url = formType === 'loan_emergency' ? '/applications/emergency' : '/applications'
    // ส่ง draft_id ไปด้วยเพื่อให้ backend migrate attachments จาก draft → loan_application
    const payload = { ...data, ...(draftId ? { draft_id: draftId } : {}) }
    const response = await api.post<SubmitResponse>(url, payload)
    return response.data
  },

  async getMyApplications(): Promise<ApplicationListItem[]> {
    const response = await api.get<ApplicationListItem[]>('/applications/me')
    return response.data
  },

  async getById(id: string): Promise<ApplicationDetail> {
    const response = await api.get<ApplicationDetail>(`/applications/${id}`)
    return response.data
  },

  async cancel(id: string, reason?: string): Promise<{ success: boolean; message: string }> {
    const response = await api.post(`/applications/${id}/cancel`, { reason: reason ?? null })
    return response.data
  },

  async resubmit(id: string): Promise<{ success: boolean; message: string }> {
    const response = await api.post(`/applications/${id}/resubmit`)
    return response.data
  },
}

export default applicationService
