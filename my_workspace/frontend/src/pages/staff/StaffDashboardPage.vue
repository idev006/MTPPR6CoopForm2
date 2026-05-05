<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import StatCard from '@/components/StatCard.vue'
import { staffService, type StaffApplication } from '@/services/staff.service'

const router = useRouter()
const allApplications = ref<StaffApplication[]>([])
const loading = ref(true)
const error = ref('')

const STATUS_TABS = [
  { key: '', label: 'ทั้งหมด' },
  { key: 'submitted', label: 'รอดำเนินการ' },
  { key: 'under_review', label: 'กำลังตรวจสอบ' },
  { key: 'pending_documents', label: 'รอเอกสารเพิ่ม' },
  { key: 'approved', label: 'อนุมัติแล้ว' },
  { key: 'rejected', label: 'ปฏิเสธ' },
] as const

const activeTab = ref<string>('')

onMounted(() => loadApplications())

watch(activeTab, () => loadApplications())

async function loadApplications() {
  loading.value = true
  error.value = ''
  try {
    allApplications.value = await staffService.getApplications(activeTab.value || undefined)
  } catch {
    error.value = 'ไม่สามารถดึงข้อมูลคำขอได้'
  } finally {
    loading.value = false
  }
}

// Stats always computed from all-status fetch (re-fetch on mount without filter)
const stats = computed(() => {
  const apps = allApplications.value
  return {
    total: apps.length,
    pending: apps.filter(a => a.status === 'submitted' || a.status === 'under_review' || a.status === 'pending_documents').length,
    approved: apps.filter(a => a.status === 'approved').length,
  }
})

const STATUS_LABEL: Record<string, string> = {
  submitted: 'รอดำเนินการ',
  under_review: 'กำลังตรวจสอบ',
  approved: 'อนุมัติแล้ว',
  rejected: 'ปฏิเสธ',
  pending_documents: 'รอเอกสารเพิ่ม',
}
const STATUS_CLASS: Record<string, string> = {
  submitted: 'badge-info',
  under_review: 'badge-warning',
  approved: 'badge-success',
  rejected: 'badge-error',
  pending_documents: 'badge-warning',
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('th-TH', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

function formatCurrency(val: number | null) {
  if (val == null) return '—'
  return new Intl.NumberFormat('th-TH', { style: 'currency', currency: 'THB' }).format(val)
}
</script>

<template>
  <AppLayout>
    <div class="p-6 max-w-7xl mx-auto">

      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <h1 class="text-3xl font-black tracking-tight">Staff Dashboard</h1>
            <span class="badge badge-primary font-bold">Admin Access</span>
          </div>
          <p class="text-base-content/60">ระบบจัดการและพิจารณาคำขอกู้เงินสหกรณ์</p>
        </div>
        <div class="text-sm text-base-content/40">
          ข้อมูล ณ วันที่ {{ formatDate(new Date().toISOString()) }}
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
        <StatCard
          title="คำขอที่โหลด"
          :value="allApplications.length"
          description="ตามตัวกรองที่เลือก"
          value-class="text-primary"
        />
        <StatCard
          title="รอดำเนินการ"
          :value="stats.pending"
          description="submitted / under_review / pending_docs"
          value-class="text-warning"
        />
        <StatCard
          title="อนุมัติแล้ว"
          :value="stats.approved"
          description="รายการสำเร็จ"
          value-class="text-success"
        />
      </div>

      <!-- Filter Tabs -->
      <div class="tabs tabs-boxed bg-base-200 mb-6 w-fit gap-1 p-1">
        <button
          v-for="tab in STATUS_TABS"
          :key="tab.key"
          class="tab tab-sm font-medium transition-all"
          :class="activeTab === tab.key ? 'tab-active' : ''"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Table Card -->
      <div class="card bg-base-100 shadow border border-base-200">
        <div class="card-body p-0">

          <!-- Loading -->
          <div v-if="loading" class="p-20 text-center">
            <span class="loading loading-dots loading-lg text-primary"></span>
          </div>

          <!-- Error -->
          <div v-else-if="error" class="p-10 text-center">
            <div class="alert alert-error max-w-md mx-auto">{{ error }}</div>
          </div>

          <!-- Empty -->
          <div v-else-if="allApplications.length === 0" class="p-20 text-center opacity-40">
            <p class="text-xl font-bold">ไม่มีรายการ</p>
            <p class="text-sm mt-1">ไม่พบคำขอที่ตรงกับตัวกรองนี้</p>
          </div>

          <!-- Table -->
          <div v-else class="overflow-x-auto">
            <table class="table table-zebra w-full">
              <thead class="bg-base-200/50">
                <tr>
                  <th class="py-4">เลขที่คำขอ / วันที่</th>
                  <th>ผู้กู้</th>
                  <th>ประเภท / ยอดกู้</th>
                  <th>สถานะ</th>
                  <th class="text-right">จัดการ</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="app in allApplications"
                  :key="app.id"
                  class="hover cursor-pointer"
                  @click="router.push(`/staff/applications/${app.id}`)"
                >
                  <td>
                    <div class="font-bold text-primary">{{ app.application_no }}</div>
                    <div class="text-xs opacity-50">{{ formatDate(app.submitted_at) }}</div>
                  </td>
                  <td>
                    <div class="flex items-center gap-3">
                      <div class="avatar placeholder">
                        <div class="bg-neutral text-neutral-content rounded-full w-8">
                          <span>{{ app.applicant_name.charAt(0) }}</span>
                        </div>
                      </div>
                      <span class="font-medium">{{ app.applicant_name }}</span>
                    </div>
                  </td>
                  <td>
                    <div class="badge badge-outline badge-sm mb-1 uppercase">{{ app.form_type }}</div>
                    <div class="font-bold">{{ formatCurrency(app.requested_amount) }}</div>
                  </td>
                  <td>
                    <span class="badge badge-md font-bold" :class="STATUS_CLASS[app.status] ?? 'badge-ghost'">
                      {{ STATUS_LABEL[app.status] ?? app.status }}
                    </span>
                  </td>
                  <td class="text-right">
                    <button class="btn btn-primary btn-sm btn-circle" title="ตรวจสอบ">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="p-4 border-t border-base-200 text-center text-xs text-base-content/30">
            แสดงล่าสุดสูงสุด 50 รายการ · กดแถวเพื่อดูรายละเอียด
          </div>
        </div>
      </div>

    </div>
  </AppLayout>
</template>
