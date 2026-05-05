export interface AddressInfo {
  house_no: string
  moo: string
  road: string
  tambon: string
  amphur: string
  province: string
}

export interface Step1Data {
  title: string
  first_name: string
  last_name: string
  id_card: string
  position: string
  department: string
  organization: string
  phone: string
  member_code: string
  marital_status: 'single' | 'married'
  spouse_name?: string
  // ที่อยู่ปัจจุบัน
  current_addr: AddressInfo
  // ที่อยู่ตามทะเบียนบ้าน
  register_addr: AddressInfo
  // ข้อมูลรายได้
  salary: number | null
  shares_amount: number | null
  existing_debt: number | null
}

export interface Step2Data {
  loan_amount: number | null
  loan_purpose: string
  repayment_period: number | null
  payout_method: 'transfer' | 'cash' | 'cheque'
  bank_name?: string
  bank_account_no?: string
  bank_account_name?: string
}

export interface StepEmergencyData {
  loan_amount: number | null
  loan_purpose: string
  repayment_period: number | null
  payout_method: 'transfer' | 'cash'
}

export interface GuarantorInfo {
  name: string
  id_card: string
  position: string
  department: string
  phone: string
  member_code?: string
  current_addr: AddressInfo
  marital_status: 'single' | 'married'
  spouse_name?: string
}

export interface Step3Data {
  guarantors: GuarantorInfo[] // Support 1-3 people
}

export interface SignatureData {
  signed: boolean
  signed_at?: string
  signature_base64?: string
  signer_name?: string
  signer_position?: string
}

export interface Step4Data {
  borrower_sig: SignatureData
  spouse_sig: SignatureData
  guarantor_sigs: SignatureData[]
  guarantor_spouse_sigs: SignatureData[] // New: for guarantor's spouse
  superior_sig: SignatureData
  superior_opinion: 'true' | 'false' | null
}

export interface Step5Data {
  checklist_items: boolean[] // 18 items
  limit_analysis: {
    total_income: number
    total_deduction: number
    net_income: number
  }
}

export interface Step6Data {
  contract_no: string
  interest_rate: number
  effective_date: string
  manager_sig: SignatureData
  chairman_sig: SignatureData
  witness_sig_1: SignatureData
  witness_sig_2: SignatureData
  // ชื่อ-นามสกุลสำหรับ PDF mapping
  manager_name: string
  chairman_name: string
  witness_1_name: string
  witness_2_name: string
}

export interface LoanOrdinaryFormData {
  step1: Step1Data
  step2: Step2Data
  step3: Step3Data
  step4: Step4Data
  step5: Step5Data
  step6: Step6Data
}

export interface LoanEmergencyFormData {
  step1: Step1Data
  step2: StepEmergencyData
  step4: Step4Data
}
