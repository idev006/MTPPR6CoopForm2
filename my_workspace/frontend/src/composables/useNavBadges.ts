import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { staffService } from '@/services/staff.service'
import type { StaffBadgeKey } from '@/configs/navigation'

const POLL_INTERVAL = 60_000

export function useNavBadges() {
  const auth = useAuthStore()
  const badges = ref<Record<StaffBadgeKey, number>>({
    submitted: 0,
    under_review: 0,
    pending_documents: 0,
  })

  let timer: ReturnType<typeof setInterval> | null = null

  async function fetchBadges() {
    if (auth.user?.role !== 'staff') return
    try {
      const [submitted, underReview, pendingDocs] = await Promise.allSettled([
        staffService.getApplications('submitted'),
        staffService.getApplications('under_review'),
        staffService.getApplications('pending_documents'),
      ])
      badges.value = {
        submitted:         submitted.status === 'fulfilled' ? submitted.value.length : 0,
        under_review:      underReview.status === 'fulfilled' ? underReview.value.length : 0,
        pending_documents: pendingDocs.status === 'fulfilled' ? pendingDocs.value.length : 0,
      }
    } catch {
      // silent — badge หายไม่กระทบการใช้งาน
    }
  }

  onMounted(() => {
    fetchBadges()
    timer = setInterval(fetchBadges, POLL_INTERVAL)
  })

  onUnmounted(() => {
    if (timer) clearInterval(timer)
  })

  return { badges }
}
