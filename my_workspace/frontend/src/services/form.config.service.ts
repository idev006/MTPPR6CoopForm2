import api from './api.service'

export interface StepDef {
  id: string
  label: string
  component: string
  store_key: string
  roles: string[]
}

export interface FormConfig {
  form_id: string
  meta: Record<string, any>
  steps: StepDef[]
}

export const formConfigService = {
  async get(formId: string): Promise<FormConfig> {
    const res = await api.get<FormConfig>(`/forms/${formId}/config`)
    return res.data
  },
}
