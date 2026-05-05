export interface DraftSession {
  id: string
  user_id: string
  form_type: string
  form_data: Record<string, unknown>
  current_step: number
  last_saved_at: string
  expires_at: string
}

export interface DraftUpdate {
  form_data?: Record<string, unknown> | object
  current_step?: number
}
