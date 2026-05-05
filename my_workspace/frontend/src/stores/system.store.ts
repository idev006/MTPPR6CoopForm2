import { defineStore } from 'pinia'
import api from '@/services/api.service'

export const useSystemStore = defineStore('system', {
  state: () => ({
    config: {
      storage: {
        max_size_mb: 10,
        allowed_mimes: ['application/pdf']
      },
      validation: {
        enabled: true,
        check_file_size: true,
        check_file_type: true
      }
    },
    stats: {
      database: { total_applications: 0, total_users: 0, pending_review: 0 },
      storage: { attachment_count: 0, attachment_total_size_mb: 0 },
      system: { status: 'Unknown', environment: 'production' }
    },
    loaded: false
  }),

  actions: {
    async fetchConfig() {
      try {
        const res = await api.get('/system/config')
        this.config = res.data
      } catch (err) {
        console.error('Failed to fetch system config', err)
      }
    },

    async fetchStats() {
      try {
        const res = await api.get('/system/stats')
        this.stats = res.data
        this.loaded = true
      } catch (err) {
        console.error('Failed to fetch system stats', err)
      }
    },

    async clearCache() {
      const toast = await import('@/stores/toast.store').then(m => m.useToastStore())
      try {
        const res = await api.post('/system/clear-cache')
        if (res.data.success) {
          toast.show('ล้างไฟล์แคชเรียบร้อยแล้ว', 'success')
          await this.fetchStats()
        }
      } catch (err) {
        toast.show('ไม่สามารถล้างแคชได้', 'error')
      }
    },

    async triggerBackup() {
      const toast = await import('@/stores/toast.store').then(m => m.useToastStore())
      try {
        const res = await api.post('/system/backup')
        if (res.data.success) {
          toast.show('สำรองข้อมูลเรียบร้อยแล้ว', 'success')
        }
      } catch (err) {
        toast.show('ไม่สามารถสำรองข้อมูลได้', 'error')
      }
    }
  }
})
