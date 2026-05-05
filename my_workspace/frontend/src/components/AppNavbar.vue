<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useAuth } from '@/composables/useAuth'
import ThemePicker from './ThemePicker.vue'
import NotificationBell from './layout/NotificationBell.vue'
import { NAV_ITEMS } from '@/configs/navigation'

const auth = useAuthStore()
const { logout } = useAuth()
const router = useRouter()

// Filter menu items based on current user's role
const menuItems = computed(() => {
  return NAV_ITEMS.filter(item => auth.hasRole(item.roles))
})
</script>

<template>
  <div class="navbar bg-base-100 shadow-sm px-4">
    <div class="flex-1 flex items-center gap-4">
      <a class="text-lg font-bold cursor-pointer" @click="router.push('/')">CoopForm</a>
      
      <!-- Dynamic Desktop Menu -->
      <div class="hidden md:flex gap-1">
        <button 
          v-for="item in menuItems" 
          :key="item.path"
          class="btn btn-ghost btn-sm font-normal"
          :class="{ 'btn-active bg-base-200': router.currentRoute.value.path === item.path }"
          @click="router.push(item.path)"
        >
          {{ item.label }}
        </button>
      </div>
    </div>

    <div class="flex-none flex items-center gap-1">
      <NotificationBell v-if="auth.user" />
      <ThemePicker />
      <div class="dropdown dropdown-end">
        <div tabindex="0" role="button" class="btn btn-ghost btn-sm gap-2">
          <div class="avatar placeholder">
            <div class="bg-neutral text-neutral-content rounded-full w-7">
              <span class="text-xs">{{ auth.user?.first_name?.[0] }}</span>
            </div>
          </div>
          <span class="hidden sm:inline text-sm">{{ auth.user?.first_name }}</span>
        </div>
        <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-box shadow-lg z-50 w-48 p-1 border border-base-300 mt-1">
          <li class="px-3 py-2 border-b border-base-200 mb-1">
            <div class="text-xs text-base-content/60 font-normal pointer-events-none truncate">
              {{ auth.user?.email }}
            </div>
            <div class="badge badge-neutral badge-sm mt-0.5">
              {{ auth.roleLabel }}
            </div>
          </li>
          
          <!-- Dynamic Mobile Menu (visible inside dropdown) -->
          <li v-for="item in menuItems" :key="item.path" class="md:hidden">
            <a @click="router.push(item.path)">{{ item.label }}</a>
          </li>
          <div v-if="menuItems.length > 0" class="divider my-0 md:hidden"></div>

          <li><a @click="router.push('/profile')">ข้อมูลส่วนตัว</a></li>
          <li><a class="text-error" @click="logout">ออกจากระบบ</a></li>
        </ul>
      </div>
    </div>
  </div>
</template>
