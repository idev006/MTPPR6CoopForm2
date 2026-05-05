export const ROLES = {
  BORROWER: 'borrower',
  STAFF: 'staff',
} as const

export type UserRole = typeof ROLES[keyof typeof ROLES]

export const ROLE_LABELS: Record<UserRole, string> = {
  [ROLES.BORROWER]: 'สมาชิก',
  [ROLES.STAFF]: 'เจ้าหน้าที่',
}
