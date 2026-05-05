export interface MemberProfile {
  id: string
  email: string
  member_code: string | null
  national_id: string | null
  first_name: string
  last_name: string
  role: string
  title: string | null
  position: string | null
  department: string | null
  organization: string | null
  phone: string | null
  addr_house_no: string | null
  addr_moo: string | null
  addr_road: string | null
  addr_tambon: string | null
  addr_amphur: string | null
  addr_province: string | null
  salary: number | null
  shares_amount: number | null
  existing_debt: number | null
  updated_at: string | null
}

export interface MemberProfileUpdate {
  title?: string | null
  position?: string | null
  department?: string | null
  organization?: string | null
  phone?: string | null
  addr_house_no?: string | null
  addr_moo?: string | null
  addr_road?: string | null
  addr_tambon?: string | null
  addr_amphur?: string | null
  addr_province?: string | null
}
