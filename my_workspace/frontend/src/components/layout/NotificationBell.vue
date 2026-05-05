<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/stores/notification.store'
import { useAuthStore } from '@/stores/auth.store'

const notifStore = useNotificationStore()
const auth = useAuthStore()
const router = useRouter()
const isOpen = ref(false)

// Staff polls more frequently — they need near-real-time awareness of new submissions
const POLL_INTERVAL = auth.user?.role === 'staff' ? 30_000 : 60_000

let timer: ReturnType<typeof setInterval>

onMounted(() => {
  notifStore.fetchNotifications()
  timer = setInterval(() => notifStore.fetchNotifications(), POLL_INTERVAL)
})

onUnmounted(() => clearInterval(timer))

async function handleNotifClick(notif: any) {
  await notifStore.markAsRead(notif.id)
  isOpen.value = false
  if (notif.link) router.push(notif.link)
}

function closeOnOutsideClick() {
  if (isOpen.value) isOpen.value = false
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('th-TH', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  })
}

// Icon per notification type
const TYPE_DOT: Record<string, string> = {
  success:  'bg-success',
  error:    'bg-error',
  warning:  'bg-warning',
  info:     'bg-info',
}

// Short prefix label in the list
const TYPE_LABEL: Record<string, string> = {
  success:  'อนุมัติ',
  error:    'ไม่อนุมัติ',
  warning:  'แจ้งเตือน',
  info:     'ข้อมูล',
}

const TYPE_BADGE: Record<string, string> = {
  success:  'badge-success',
  error:    'badge-error',
  warning:  'badge-warning',
  info:     'badge-info',
}
</script>

<template>
  <!-- click-outside overlay -->
  <div v-if="isOpen" class="fixed inset-0 z-40" @click="closeOnOutsideClick" />

  <div class="relative z-50">
    <!-- Bell button -->
    <button
      class="btn btn-ghost btn-circle"
      :title="`การแจ้งเตือน${notifStore.unreadCount > 0 ? ` (${notifStore.unreadCount} ใหม่)` : ''}`"
      @click="isOpen = !isOpen"
    >
      <div class="indicator">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        <span
          v-if="notifStore.unreadCount > 0"
          class="badge badge-xs badge-primary indicator-item"
        >
          {{ notifStore.unreadCount > 9 ? '9+' : notifStore.unreadCount }}
        </span>
      </div>
    </button>

    <!-- Dropdown panel -->
    <div
      v-if="isOpen"
      class="absolute right-0 mt-2 w-80 bg-base-100 shadow-2xl border border-base-200 rounded-box overflow-hidden"
    >
      <!-- Header -->
      <div class="flex justify-between items-center px-4 py-3 bg-base-200/60 border-b border-base-200">
        <div class="flex items-center gap-2">
          <span class="font-black text-xs uppercase tracking-widest">การแจ้งเตือน</span>
          <span v-if="notifStore.unreadCount > 0" class="badge badge-primary badge-xs">
            {{ notifStore.unreadCount }} ใหม่
          </span>
        </div>
        <button
          class="text-[10px] font-bold text-primary hover:underline"
          @click="notifStore.markAllAsRead()"
        >
          อ่านทั้งหมด
        </button>
      </div>

      <!-- Notification list -->
      <div class="max-h-96 overflow-y-auto divide-y divide-base-100">

        <div v-if="notifStore.notifications.length === 0"
          class="p-10 text-center text-xs text-base-content/30 italic">
          ไม่มีการแจ้งเตือนในขณะนี้
        </div>

        <div
          v-for="notif in notifStore.notifications"
          :key="notif.id"
          class="flex gap-3 px-4 py-3 hover:bg-base-200/60 cursor-pointer transition-colors"
          :class="{ 'bg-primary/5': !notif.is_read }"
          @click="handleNotifClick(notif)"
        >
          <!-- Type dot -->
          <div class="pt-1.5 shrink-0">
            <span
              class="block w-2 h-2 rounded-full"
              :class="notif.is_read ? 'bg-base-300' : (TYPE_DOT[notif.type] ?? 'bg-info')"
            />
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-1">
              <p class="text-xs font-bold leading-tight line-clamp-1"
                :class="{ 'text-base-content': notif.is_read, 'text-primary': !notif.is_read }">
                {{ notif.title }}
              </p>
              <span
                class="badge badge-xs shrink-0 mt-0.5"
                :class="TYPE_BADGE[notif.type] ?? 'badge-ghost'"
              >
                {{ TYPE_LABEL[notif.type] ?? notif.type }}
              </span>
            </div>
            <p class="text-[11px] text-base-content/60 mt-1 line-clamp-2">{{ notif.message }}</p>
            <p class="text-[10px] font-medium text-base-content/30 mt-1">{{ formatDate(notif.created_at) }}</p>
          </div>
        </div>

      </div>

      <!-- Footer -->
      <div class="px-4 py-2 border-t border-base-200 bg-base-200/30 text-center">
        <button class="btn btn-ghost btn-xs w-full text-[10px]" @click="isOpen = false">ปิด</button>
      </div>
    </div>
  </div>
</template>
