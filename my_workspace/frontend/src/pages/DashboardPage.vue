<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useToastStore } from '@/stores/toast.store'
import { useConfirmStore } from '@/stores/confirm.store'
import AppLayout from '@/components/AppLayout.vue'
import DashboardActionCard from '@/components/DashboardActionCard.vue'
import { applicationService, type ApplicationListItem } from '@/services/application.service'
import { draftService } from '@/services/draft.service'
import type { DraftSession } from '@/types/draft'

const auth = useAuthStore()
const toast = useToastStore()
const confirmStore = useConfirmStore()
const router = useRouter()

// ── Applications ──────────────────────────────────────────────
const applications = ref<ApplicationListItem[]>([])
const loadingApps = ref(true)

// ── Drafts ────────────────────────────────────────────────────
const drafts = ref<DraftSession[]>([])
const loadingDrafts = ref(true)
const discardingId = ref<string | null>(null)

const hasDrafts = computed(() => drafts.value.length > 0)

// แยก active กับ ปิดแล้ว
const ACTIVE_STATUSES = ['submitted', 'under_review', 'pending_documents', 'approved']
const CLOSED_STATUSES = ['cancelled', 'rejected']

const activeApplications = computed(() =>
  applications.value.filter(a => ACTIVE_STATUSES.includes(a.status))
)
const closedApplications = computed(() =>
  applications.value.filter(a => CLOSED_STATUSES.includes(a.status))
)
const showClosedSection = ref(false)

const FORM_TYPE_META: Record<string, { label: string; route: string; stepTotal: number }> = {
  loan_ordinary: { label: 'กู้สามัญ', route: 'application-ordinary-new', stepTotal: 8 },
  loan_emergency: { label: 'กู้ฉุกเฉิน', route: 'application-emergency-new', stepTotal: 6 },
}

const statusLabel: Record<string, string> = {
  submitted: 'รออนุมัติ',
  under_review: 'กำลังพิจารณา',
  pending_documents: 'รอเอกสารเพิ่ม',
  approved: 'อนุมัติแล้ว',
  rejected: 'ไม่อนุมัติ',
  cancelled: 'ยกเลิกแล้ว',
}

const statusClass: Record<string, string> = {
  submitted: 'badge-info',
  under_review: 'badge-warning',
  pending_documents: 'badge-warning',
  approved: 'badge-success',
  rejected: 'badge-error',
  cancelled: 'badge-neutral',
}

const formTypeLabel: Record<string, string> = {
  loan_ordinary: 'กู้สามัญ',
  loan_emergency: 'กู้ฉุกเฉิน',
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('th-TH', { year: 'numeric', month: 'short', day: 'numeric' })
}

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString('th-TH', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

// ── Load data ─────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([loadApplications(), loadDrafts()])
})

async function loadApplications() {
  loadingApps.value = true
  try {
    applications.value = await applicationService.getMyApplications()
  } catch {
    // silent
  } finally {
    loadingApps.value = false
  }
}

async function loadDrafts() {
  loadingDrafts.value = true
  try {
    const results = await Promise.allSettled([
      draftService.getByFormType('loan_ordinary'),
      draftService.getByFormType('loan_emergency'),
    ])
    drafts.value = results
      .filter((r): r is PromiseFulfilledResult<DraftSession> => r.status === 'fulfilled' && r.value !== null)
      .map(r => r.value)
  } finally {
    loadingDrafts.value = false
  }
}

// ── Actions ───────────────────────────────────────────────────
function continueDraft(draft: DraftSession) {
  const meta = FORM_TYPE_META[draft.form_type]
  if (meta) router.push({ name: meta.route })
}

async function discardDraft(draft: DraftSession) {
  const label = FORM_TYPE_META[draft.form_type]?.label ?? ''
  const ok = await confirmStore.confirm(
    `ต้องการลบร่างคำขอ${label}นี้ใช่ไหม?\nข้อมูลที่กรอกไว้จะหายทั้งหมด`,
    { title: 'ลบร่างคำขอ', confirmLabel: 'ลบร่าง', confirmClass: 'btn-error' }
  )
  if (!ok) return
  discardingId.value = draft.id
  try {
    await draftService.delete(draft.id)
    drafts.value = drafts.value.filter(d => d.id !== draft.id)
    toast.success('ลบร่างคำขอเรียบร้อยแล้ว')
  } catch {
    toast.error('ไม่สามารถลบร่างได้ กรุณาลองใหม่')
  } finally {
    discardingId.value = null
  }
}

function startNew(formType: 'loan_ordinary' | 'loan_emergency') {
  const meta = FORM_TYPE_META[formType]
  if (meta) router.push({ name: meta.route })
}
</script>

<template>
  <AppLayout>
    <div class="p-6 md:p-8 max-w-4xl mx-auto">

      <!-- Header -->
      <h1 class="text-2xl font-bold">
        ยินดีต้อนรับ คุณ{{ auth.user?.first_name }} {{ auth.user?.last_name }}
      </h1>
      <p class="mt-1 text-base-content/60">ระบบกรอกแบบฟอร์มขอกู้เงินสหกรณ์</p>

      <!-- ── Draft resume section ─────────────────────────────── -->
      <div v-if="loadingDrafts" class="mt-6">
        <div class="skeleton h-28 w-full rounded-xl"></div>
      </div>

      <div v-else-if="hasDrafts" class="mt-6 space-y-3">
        <h2 class="text-sm font-semibold text-warning flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
          </svg>
          คำขอที่ยังค้างอยู่
        </h2>

        <div
          v-for="draft in drafts"
          :key="draft.id"
          class="card bg-warning/10 border border-warning/30 shadow-sm"
        >
          <div class="card-body p-4 flex flex-row items-center justify-between gap-4 flex-wrap">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="badge badge-warning badge-sm">ร่าง</span>
                <span class="font-semibold text-base-content">
                  คำขอ{{ FORM_TYPE_META[draft.form_type]?.label ?? draft.form_type }}
                </span>
              </div>
              <p class="text-xs text-base-content/60">
                บันทึกล่าสุด: {{ formatDateTime(draft.last_saved_at) }}
              </p>
              <!-- Step progress bar -->
              <div class="mt-2 flex items-center gap-2">
                <progress
                  class="progress progress-warning w-32 h-1.5"
                  :value="draft.current_step"
                  :max="FORM_TYPE_META[draft.form_type]?.stepTotal ?? 8"
                ></progress>
                <span class="text-xs text-base-content/50">
                  ขั้นตอนที่ {{ draft.current_step }} / {{ FORM_TYPE_META[draft.form_type]?.stepTotal ?? 8 }}
                </span>
              </div>
            </div>

            <div class="flex gap-2 shrink-0">
              <button
                class="btn btn-warning btn-sm"
                @click="continueDraft(draft)"
              >
                ดำเนินการต่อ →
              </button>
              <button
                class="btn btn-ghost btn-sm text-error"
                :disabled="discardingId === draft.id"
                @click="discardDraft(draft)"
              >
                <span v-if="discardingId === draft.id" class="loading loading-spinner loading-xs"></span>
                <span v-else>ลบร่าง</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Action cards ─────────────────────────────────────── -->
      <div class="mt-6">
        <h2 class="text-sm font-semibold text-base-content/60 mb-3">
          {{ hasDrafts ? 'เริ่มคำขอใหม่' : 'ยื่นคำขอกู้เงิน' }}
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <DashboardActionCard
            title="ยื่นคำขอกู้สามัญ"
            description="กรอกแบบฟอร์มขอกู้เงินสามัญตามระเบียบสหกรณ์"
            action-label="เริ่มดำเนินการ"
            @action="startNew('loan_ordinary')"
          />
          <DashboardActionCard
            title="ยื่นคำขอกู้ฉุกเฉิน"
            description="บรรเทาความเดือดร้อนเร่งด่วน วงเงินสูงสุด 50,000 บาท"
            action-label="เริ่มดำเนินการ"
            variant="secondary"
            @action="startNew('loan_emergency')"
          />
        </div>
      </div>

      <!-- ── Application history ──────────────────────────────── -->
      <div class="mt-10">
        <h2 class="text-lg font-semibold mb-4">ประวัติคำขอ</h2>

        <div v-if="loadingApps" class="flex justify-center py-8">
          <span class="loading loading-spinner loading-md"></span>
        </div>

        <template v-else>
          <!-- ไม่มีคำขอเลย -->
          <div v-if="applications.length === 0" class="card bg-base-100 shadow-sm">
            <div class="card-body items-center text-center py-12 text-base-content/50">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mb-2 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p>ยังไม่มีประวัติคำขอ</p>
            </div>
          </div>

          <!-- Active applications -->
          <div v-if="activeApplications.length > 0" class="card bg-base-100 shadow-sm overflow-hidden">
            <div class="overflow-x-auto">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>หมายเลขคำขอ</th>
                    <th>ประเภท</th>
                    <th>สถานะ</th>
                    <th>วันที่ยื่น</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="app in activeApplications"
                    :key="app.id"
                    class="hover cursor-pointer"
                    @click="router.push({ name: 'application-detail', params: { id: app.id } })"
                  >
                    <td class="font-mono font-medium">{{ app.application_no }}</td>
                    <td>{{ formTypeLabel[app.form_type] ?? app.form_type }}</td>
                    <td>
                      <span class="badge badge-sm" :class="statusClass[app.status] ?? 'badge-ghost'">
                        {{ statusLabel[app.status] ?? app.status }}
                      </span>
                    </td>
                    <td class="text-base-content/60 text-xs">{{ formatDate(app.created_at) }}</td>
                    <td>
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-base-content/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                      </svg>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Closed applications (cancelled + rejected) — collapsible -->
          <div v-if="closedApplications.length > 0" class="mt-4">
            <button
              class="flex items-center gap-2 text-sm text-base-content/50 hover:text-base-content transition-colors"
              @click="showClosedSection = !showClosedSection"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 transition-transform"
                :class="showClosedSection ? 'rotate-90' : ''"
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
              รายการที่ปิดแล้ว ({{ closedApplications.length }})
            </button>

            <div v-if="showClosedSection" class="mt-2 card bg-base-100 shadow-sm overflow-hidden opacity-70">
              <div class="overflow-x-auto">
                <table class="table table-sm">
                  <thead>
                    <tr>
                      <th>หมายเลขคำขอ</th>
                      <th>ประเภท</th>
                      <th>สถานะ</th>
                      <th>วันที่ยื่น</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="app in closedApplications"
                      :key="app.id"
                      class="hover cursor-pointer"
                      @click="router.push({ name: 'application-detail', params: { id: app.id } })"
                    >
                      <td class="font-mono font-medium">{{ app.application_no }}</td>
                      <td>{{ formTypeLabel[app.form_type] ?? app.form_type }}</td>
                      <td>
                        <span class="badge badge-sm" :class="statusClass[app.status] ?? 'badge-ghost'">
                          {{ statusLabel[app.status] ?? app.status }}
                        </span>
                      </td>
                      <td class="text-base-content/60 text-xs">{{ formatDate(app.created_at) }}</td>
                      <td>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-base-content/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </template>
      </div>

    </div>
  </AppLayout>
</template>
