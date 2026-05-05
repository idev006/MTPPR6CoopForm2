import { ROLES, type UserRole } from '@/constants/roles'

export type StaffBadgeKey = 'submitted' | 'under_review' | 'pending_documents'

export interface NavItem {
  type: 'item'
  label: string
  path: string
  roles: UserRole[]
  icon: string
  exact?: boolean
  badgeKey?: StaffBadgeKey
}

export interface NavGroup {
  type: 'group'
  label: string
  icon: string
  roles: UserRole[]
  defaultOpen?: boolean
  children: NavItem[]
}

export type NavEntry = NavItem | NavGroup

// ── Borrower Navigation ───────────────────────────────────────
const BORROWER_NAV: NavEntry[] = [
  {
    type: 'item',
    label: 'หน้าหลัก',
    path: '/',
    roles: [ROLES.BORROWER],
    icon: '🏠',
    exact: true,
  },
  {
    type: 'group',
    label: 'ยื่นคำขอกู้',
    icon: '📝',
    roles: [ROLES.BORROWER],
    defaultOpen: true,
    children: [
      {
        type: 'item',
        label: 'กู้สามัญ',
        path: '/applications/ordinary/new',
        roles: [ROLES.BORROWER],
        icon: '📄',
      },
      {
        type: 'item',
        label: 'กู้ฉุกเฉิน',
        path: '/applications/emergency/new',
        roles: [ROLES.BORROWER],
        icon: '⚡',
      },
    ],
  },
  {
    type: 'item',
    label: 'โปรไฟล์',
    path: '/profile',
    roles: [ROLES.BORROWER],
    icon: '👤',
  },
]

// ── Staff Navigation ──────────────────────────────────────────
const STAFF_NAV: NavEntry[] = [
  {
    type: 'item',
    label: 'ภาพรวม',
    path: '/staff',
    roles: [ROLES.STAFF],
    icon: '🏠',
    exact: true,
  },
  {
    type: 'item',
    label: 'รอดำเนินการ',
    path: '/staff?status=submitted',
    roles: [ROLES.STAFF],
    icon: '📥',
    badgeKey: 'submitted',
  },
  {
    type: 'item',
    label: 'กำลังพิจารณา',
    path: '/staff?status=under_review',
    roles: [ROLES.STAFF],
    icon: '🔍',
    badgeKey: 'under_review',
  },
  {
    type: 'item',
    label: 'รอเอกสารเพิ่ม',
    path: '/staff?status=pending_documents',
    roles: [ROLES.STAFF],
    icon: '📎',
    badgeKey: 'pending_documents',
  },
  {
    type: 'item',
    label: 'อนุมัติแล้ว',
    path: '/staff?status=approved',
    roles: [ROLES.STAFF],
    icon: '✅',
  },
  {
    type: 'item',
    label: 'ปฏิเสธแล้ว',
    path: '/staff?status=rejected',
    roles: [ROLES.STAFF],
    icon: '❌',
  },
  {
    type: 'item',
    label: 'ยกเลิกแล้ว',
    path: '/staff?status=cancelled',
    roles: [ROLES.STAFF],
    icon: '🚫',
  },
  {
    type: 'item',
    label: 'จัดการสมาชิก',
    path: '/staff/members',
    roles: [ROLES.STAFF],
    icon: '👥',
  },
  {
    type: 'item',
    label: 'System Cockpit',
    path: '/staff/cockpit',
    roles: [ROLES.STAFF],
    icon: '⚙️',
  },
]

export const NAV_ENTRIES: NavEntry[] = [...BORROWER_NAV, ...STAFF_NAV]

// Legacy flat list — ใช้โดย AppNavbar.vue (deprecated)
export const NAV_ITEMS = [
  { label: 'แดชบอร์ด', path: '/', roles: [ROLES.BORROWER] },
  { label: 'ยื่นคำขอกู้เงิน', path: '/applications/new', roles: [ROLES.BORROWER] },
  { label: 'รายการคำขอ (Staff)', path: '/staff', roles: [ROLES.STAFF] },
]
