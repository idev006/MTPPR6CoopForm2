<template>
  <nav class="lg:hidden fixed bottom-0 left-0 right-0 z-30 bg-base-100 border-t border-base-300">
    <div class="flex items-center justify-around h-16">
      <template v-for="item in bottomItems" :key="item.path">
        <RouterLink
          :to="item.path"
          class="flex flex-col items-center gap-0.5 px-3 py-1 rounded-lg transition-colors min-w-[56px]"
          :class="isActive(item) ? 'text-primary' : 'text-base-content/50'"
        >
          <span class="text-xl leading-none relative">
            {{ item.icon }}
            <span
              v-if="item.badgeKey && badges[item.badgeKey] > 0"
              class="absolute -top-1 -right-1.5 bg-error text-white text-[9px] font-bold rounded-full min-w-[14px] h-3.5 flex items-center justify-center px-0.5"
            >
              {{ badges[item.badgeKey] > 9 ? '9+' : badges[item.badgeKey] }}
            </span>
          </span>
          <span class="text-[10px] font-medium leading-tight">{{ item.label }}</span>
        </RouterLink>
      </template>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useNavBadges } from '@/composables/useNavBadges'
import { ROLES } from '@/constants/roles'
import type { NavItem } from '@/configs/navigation'

const auth = useAuthStore()
const route = useRoute()
const { badges } = useNavBadges()

// Bottom nav แสดงแค่ 4 รายการหลัก
const BORROWER_BOTTOM: NavItem[] = [
  { type: 'item', label: 'หน้าหลัก',  path: '/',                         icon: '🏠', roles: [ROLES.BORROWER], exact: true },
  { type: 'item', label: 'ยื่นคำขอ',  path: '/applications/ordinary/new', icon: '📝', roles: [ROLES.BORROWER] },
  { type: 'item', label: 'โปรไฟล์',   path: '/profile',                   icon: '👤', roles: [ROLES.BORROWER] },
]

const STAFF_BOTTOM: NavItem[] = [
  { type: 'item', label: 'ภาพรวม',    path: '/staff',                          icon: '🏠', roles: [ROLES.STAFF], exact: true },
  { type: 'item', label: 'รอดำเนินการ', path: '/staff?status=submitted',       icon: '📥', roles: [ROLES.STAFF], badgeKey: 'submitted' },
  { type: 'item', label: 'รอเอกสาร',  path: '/staff?status=pending_documents', icon: '📎', roles: [ROLES.STAFF], badgeKey: 'pending_documents' },
  { type: 'item', label: 'Cockpit',   path: '/staff/cockpit',                  icon: '⚙️', roles: [ROLES.STAFF] },
]

const bottomItems = computed(() =>
  auth.user?.role === 'staff' ? STAFF_BOTTOM : BORROWER_BOTTOM
)

function isActive(item: NavItem): boolean {
  if (item.exact) return route.path === item.path && !route.query.status
  if (item.path.includes('?status=')) {
    const [basePath, status] = item.path.split('?status=')
    return route.path === basePath && route.query.status === status
  }
  return route.path.startsWith(item.path)
}
</script>
