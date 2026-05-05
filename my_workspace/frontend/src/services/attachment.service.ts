import api from './api.service'

export interface Attachment {
  id: string
  file_type: string
  original_filename: string
  file_size_bytes: number | null
  mime_type?: string | null
  uploaded_at?: string
}

export const attachmentService = {
  async list(applicationId: string): Promise<Attachment[]> {
    const res = await api.get<Attachment[]>(`/attachments/applications/${applicationId}`)
    return res.data
  },

  async upload(applicationId: string, file: File, fileType: string): Promise<void> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_type', fileType)
    await api.post(`/attachments/applications/${applicationId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  async remove(id: string): Promise<void> {
    await api.delete(`/attachments/${id}`)
  },

  async openFile(id: string): Promise<void> {
    const res = await api.get(`/attachments/${id}/download`, { responseType: 'blob' })
    const mime = (res.headers['content-type'] as string) || 'application/octet-stream'
    const url = URL.createObjectURL(new Blob([res.data], { type: mime }))
    window.open(url, '_blank')
  },
}
