import api from './api.service';

export interface StaffApplication {
  id: string;
  application_no: string;
  applicant_name: string;
  form_type: string;
  status: string;
  submitted_at: string;
  requested_amount: number | null;
}

export interface AttachmentInfo {
  id: string;
  file_type: string;
  original_filename: string;
  mime_type: string | null;
  uploaded_at: string;
}

export interface PartyDetail {
  role: string;
  full_name: string;
  position: string | null;
  department: string | null;
  has_signature: boolean;
}

export interface ApplicationDetail {
  id: string;
  application_no: string;
  applicant_id: string;
  form_type: string;
  status: string;
  form_data: Record<string, any>;
  submitted_at: string;
  reviewed_at: string | null;
  review_remarks: string | null;
  parties: PartyDetail[];
  attachments: AttachmentInfo[];
}

export type ReviewStatus = 'approved' | 'rejected' | 'under_review' | 'pending_documents';

export interface ReviewRequest {
  status: ReviewStatus;
  remarks?: string;
}

export const staffService = {
  async getApplications(status?: string): Promise<StaffApplication[]> {
    const params = status ? { status } : {};
    const response = await api.get<StaffApplication[]>('/staff/applications', { params });
    return response.data;
  },

  async getApplicationDetail(id: string): Promise<ApplicationDetail> {
    const response = await api.get<ApplicationDetail>(`/staff/applications/${id}`);
    return response.data;
  },

  async reviewApplication(id: string, data: ReviewRequest) {
    const response = await api.post(`/staff/applications/${id}/review`, data);
    return response.data;
  },

  async openPdf(appId: string): Promise<void> {
    const res = await api.get(`/staff/applications/${appId}/pdf`, { responseType: 'blob' });
    const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
    window.open(url, '_blank');
  },

  async openAttachment(attachmentId: string): Promise<void> {
    const res = await api.get(`/attachments/${attachmentId}/download`, { responseType: 'blob' });
    const mime = (res.headers['content-type'] as string) || 'application/octet-stream';
    const url = URL.createObjectURL(new Blob([res.data], { type: mime }));
    window.open(url, '_blank');
  },
};

export default staffService;
