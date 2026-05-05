import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api.service'

export interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  is_read: boolean
  link?: string
  created_at: string
}

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  const loading = ref(false)

  const unreadCount = computed(() => 
    notifications.value.filter(n => !n.is_read).length
  )

  async function fetchNotifications() {
    loading.value = true
    try {
      const res = await api.get('/notifications/')
      notifications.value = res.data
    } catch (err) {
      console.error('Failed to fetch notifications', err)
    } finally {
      loading.value = false
    }
  }

  async function markAsRead(id: string) {
    try {
      await api.post(`/notifications/${id}/read`)
      const notif = notifications.value.find(n => n.id === id)
      if (notif) notif.is_read = true
    } catch (err) {
      console.error('Failed to mark notification as read', err)
    }
  }

  async function markAllAsRead() {
    try {
      await api.post('/notifications/read-all')
      notifications.value.forEach(n => n.is_read = true)
    } catch (err) {
      console.error('Failed to mark all as read', err)
    }
  }

  return {
    notifications,
    loading,
    unreadCount,
    fetchNotifications,
    markAsRead,
    markAllAsRead
  }
})
