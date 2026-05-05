<template>
  <!-- w-60 กำหนดความกว้าง drawer-side ใน DaisyUI -->
  <aside class="flex flex-col w-60 min-h-screen bg-base-100 border-r border-base-300">

    <!-- Logo -->
    <div class="px-4 py-5 border-b border-base-300">
      <div class="flex items-center gap-2">
        <span class="text-2xl">🏦</span>
        <div>
          <div class="font-bold text-base leading-tight">CoopForm</div>
          <div class="text-xs text-base-content/50">
            {{ auth.user?.role === 'staff' ? 'เจ้าหน้าที่' : 'สมาชิก' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation — DaisyUI menu -->
    <ul class="menu menu-sm flex-1 px-2 py-3 gap-0.5 overflow-y-auto">
      <template v-for="entry in visibleEntries" :key="entry.label">
        <NavGroup v-if="entry.type === 'group'" :group="entry" />
        <NavItem
          v-else
          :item="entry"
          :badge="entry.badgeKey ? badges[entry.badgeKey] : 0"
        />
      </template>
    </ul>

    <!-- Footer -->
    <div class="px-2 py-3 border-t border-base-300 space-y-1">

      <!-- Notification -->
      <div class="flex items-center gap-3 px-3 py-2">
        <NotificationBell />
        <span class="text-sm text-base-content/60">การแจ้งเตือน</span>
      </div>

      <!-- Theme — dropdown-top เพื่อไม่ให้เมนูยื่นออกซ้ายจอ -->
      <div class="flex items-center gap-3 px-3 py-2">
        <ThemePicker dropdown-class="dropdown-top" />
        <span class="text-sm text-base-content/60">ธีม</span>
      </div>

      <!-- User + Logout -->
      <div class="mt-1 pt-2 border-t border-base-300">
        <div class="flex items-center gap-2 px-3 py-1.5">
          <div class="avatar placeholder">
            <div class="bg-neutral text-neutral-content rounded-full w-7 shrink-0">
              <span class="text-xs">{{ auth.user?.first_name?.[0] }}</span>
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium truncate">
              {{ auth.user?.first_name }} {{ auth.user?.last_name }}
            </div>
            <div class="text-xs text-base-content/50 truncate">{{ auth.user?.email }}</div>
          </div>
        </div>
        <button
          class="w-full flex items-center gap-3 px-3 py-2 mt-1 rounded-lg text-sm text-error hover:bg-error/10 transition-colors"
          @click="logout"
        >
          <span>🚪</span>
          <span>ออกจากระบบ</span>
        </button>
      </div>

    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { useAuth } from '@/composables/useAuth'
import { NAV_ENTRIES } from '@/configs/navigation'
import { useNavBadges } from '@/composables/useNavBadges'
import NavItem from './NavItem.vue'
import NavGroup from './NavGroup.vue'
import NotificationBell from './NotificationBell.vue'
import ThemePicker from '@/components/ThemePicker.vue'

const auth = useAuthStore()
const { logout } = useAuth()
const { badges } = useNavBadges()

const visibleEntries = computed(() =>
  NAV_ENTRIES.filter(entry => auth.hasRole(entry.roles))
)
</script>
