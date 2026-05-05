<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { staffService, type ApplicationDetail, type ReviewStatus } from '@/services/staff.service'

const route = useRoute()
const router = useRouter()
const appId = route.params.id as string

const app = ref<ApplicationDetail | null>(null)
const loading = ref(true)
const loadError = ref('')

// Decision modal state
const showModal = ref(false)
const selectedStatus = ref<ReviewStatus | ''>('')
const remarks = ref('')
const submitting = ref(false)
const submitError = ref('')

onMounted(async () => {
  try {
    app.value = await staffService.getApplicationDetail(appId)
  } catch {
    loadError.value = 'ไม่สามารถโหลดข้อมูลคำขอได้'
  } finally {
    loading.value = false
  }
})

// ── Derived form data ──────────────────────────────────
const s1 = computed(() => app.value?.form_data?.step1 ?? {})
const s2 = computed(() => app.value?.form_data?.step2 ?? {})
const guarantors = computed<any[]>(() => app.value?.form_data?.step3?.guarantors ?? [])

const fullName = computed(() => `${s1.value.title ?? ''}${s1.value.first_name ?? ''} ${s1.value.last_name ?? ''}`.trim())
const loanAmount = computed(() =>
  s2.value.loan_amount ? Number(s2.value.loan_amount).toLocaleString('th-TH') + ' บาท' : '—'
)

// ── Attachments grouped by type ────────────────────────
const DOC_LABEL: Record<string, string> = {
  loan_form: 'แบบฟอร์มขอกู้ (ระบบสร้าง)',
  payroll: 'สลิปเงินเดือน / หนังสือรับรองเงินเดือน',
  id_card_borrower: 'สำเนาบัตรประชาชนผู้กู้',
  house_reg_borrower: 'สำเนาทะเบียนบ้านผู้กู้',
  id_card_spouse: 'สำเนาบัตรประชาชนคู่สมรสผู้กู้',
  house_reg_spouse: 'สำเนาทะเบียนบ้านคู่สมรสผู้กู้',
  marriage_cert: 'สำเนาทะเบียนสมรสผู้กู้',
  id_card_g1: 'สำเนาบัตรประชาชนผู้ค้ำ 1',
  house_reg_g1: 'สำเนาทะเบียนบ้านผู้ค้ำ 1',
  id_card_spouse_g1: 'สำเนาบัตรประชาชนคู่สมรสผู้ค้ำ 1',
  house_reg_spouse_g1: 'สำเนาทะเบียนบ้านคู่สมรสผู้ค้ำ 1',
  marriage_cert_g1: 'สำเนาทะเบียนสมรสผู้ค้ำ 1',
  id_card_g2: 'สำเนาบัตรประชาชนผู้ค้ำ 2',
  house_reg_g2: 'สำเนาทะเบียนบ้านผู้ค้ำ 2',
  id_card_spouse_g2: 'สำเนาบัตรประชาชนคู่สมรสผู้ค้ำ 2',
  house_reg_spouse_g2: 'สำเนาทะเบียนบ้านคู่สมรสผู้ค้ำ 2',
  marriage_cert_g2: 'สำเนาทะเบียนสมรสผู้ค้ำ 2',
  other: 'เอกสารอื่นๆ',
}

const attachmentMap = computed(() => {
  const map: Record<string, typeof app.value.attachments[0][]> = {}
  for (const a of (app.value?.attachments ?? [])) {
    ;(map[a.file_type] ??= []).push(a)
  }
  return map
})

// ── Status helpers ─────────────────────────────────────
const STATUS_LABEL: Record<string, string> = {
  submitted: 'รอดำเนินการ',
  under_review: 'กำลังตรวจสอบ',
  approved: 'อนุมัติแล้ว',
  rejected: 'ปฏิเสธ',
  pending_documents: 'รอเอกสารเพิ่มเติม',
}
const STATUS_CLASS: Record<string, string> = {
  submitted: 'badge-info',
  under_review: 'badge-warning',
  approved: 'badge-success',
  rejected: 'badge-error',
  pending_documents: 'badge-warning',
}

// ── Decision modal helpers ─────────────────────────────
const remarksRequired = computed(() =>
  selectedStatus.value === 'rejected' || selectedStatus.value === 'pending_documents'
)
const canConfirm = computed(() =>
  selectedStatus.value !== '' && (!remarksRequired.value || remarks.value.trim().length > 0)
)

const DECISION_LABEL: Record<string, string> = {
  approved: 'อนุมัติเงินกู้',
  rejected: 'ปฏิเสธคำขอ',
  pending_documents: 'ขอเอกสารเพิ่มเติม',
  under_review: 'ทำเครื่องหมายกำลังตรวจสอบ',
}
const DECISION_BTN_CLASS: Record<string, string> = {
  approved: 'btn-success',
  rejected: 'btn-error',
  pending_documents: 'btn-warning',
  under_review: 'btn-info',
}

function openDecisionModal(status: ReviewStatus) {
  selectedStatus.value = status
  remarks.value = ''
  submitError.value = ''
  showModal.value = true
}

async function confirmDecision() {
  if (!canConfirm.value || selectedStatus.value === '') return
  submitting.value = true
  submitError.value = ''
  try {
    await staffService.reviewApplication(appId, {
      status: selectedStatus.value as ReviewStatus,
      remarks: remarks.value || undefined,
    })
    showModal.value = false
    router.push('/staff')
  } catch (err: any) {
    submitError.value = err?.response?.data?.detail || 'เกิดข้อผิดพลาด กรุณาลองใหม่'
  } finally {
    submitting.value = false
  }
}

function formatDate(d: string | null) {
  if (!d) return '—'
  return new Date(d).toLocaleString('th-TH', { dateStyle: 'medium', timeStyle: 'short' })
}

const isFinalized = computed(() =>
  app.value?.status === 'approved' || app.value?.status === 'rejected'
)
</script>

<template>
  <AppLayout>
    <div class="p-4 md:p-6 max-w-7xl mx-auto">

      <!-- Breadcrumbs -->
      <div class="text-sm breadcrumbs mb-5">
        <ul>
          <li><router-link to="/staff">Staff Dashboard</router-link></li>
          <li>พิจารณาคำขอ</li>
          <li class="font-bold text-primary">{{ app?.application_no ?? '...' }}</li>
        </ul>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-24">
        <span class="loading loading-spinner loading-lg text-primary"></span>
        <p class="mt-4 text-base-content/50">กำลังโหลดข้อมูล...</p>
      </div>

      <!-- Error -->
      <div v-else-if="loadError" class="alert alert-error max-w-lg mx-auto">{{ loadError }}</div>

      <!-- Content -->
      <div v-else-if="app" class="grid grid-cols-1 xl:grid-cols-5 gap-6">

        <!-- ════ LEFT COLUMN (3/5): Structured Form Data ════ -->
        <div class="xl:col-span-3 space-y-5">

          <!-- Header Card -->
          <div class="card bg-base-100 border border-base-300">
            <div class="card-body p-5">
              <div class="flex flex-wrap justify-between items-start gap-3">
                <div>
                  <h2 class="text-2xl font-black tracking-tight">{{ app.application_no }}</h2>
                  <p class="text-sm text-base-content/50 mt-0.5">ยื่นเมื่อ {{ formatDate(app.submitted_at) }}</p>
                </div>
                <span class="badge badge-lg font-bold px-4"
                  :class="STATUS_CLASS[app.status] ?? 'badge-ghost'">
                  {{ STATUS_LABEL[app.status] ?? app.status }}
                </span>
              </div>

              <!-- Staff remarks if already reviewed -->
              <div v-if="app.review_remarks" class="mt-3 p-3 bg-base-200 rounded-lg text-sm">
                <span class="font-bold text-base-content/70">หมายเหตุเจ้าหน้าที่:</span>
                <span class="ml-2">{{ app.review_remarks }}</span>
                <span v-if="app.reviewed_at" class="ml-2 text-base-content/40 text-xs">({{ formatDate(app.reviewed_at) }})</span>
              </div>
            </div>
          </div>

          <!-- Borrower Info -->
          <div class="card bg-base-100 border border-base-300">
            <div class="card-body p-5">
              <h3 class="font-bold text-sm text-base-content/60 uppercase tracking-wide mb-3">ข้อมูลผู้กู้</h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
                <div>
                  <p class="text-base-content/50 text-xs mb-0.5">ชื่อ-นามสกุล</p>
                  <p class="font-medium">{{ fullName || '—' }}</p>
                </div>
                <div>
                  <p class="text-base-content/50 text-xs mb-0.5">รหัสสมาชิก</p>
                  <p class="font-medium">{{ s1.member_code || '—' }}</p>
                </div>
                <div>
                  <p class="text-base-content/50 text-xs mb-0.5">เลขบัตรประชาชน</p>
                  <p class="font-medium">{{ s1.id_card || '—' }}</p>
                </div>
                <div>
                  <p class="text-base-content/50 text-xs mb-0.5">ตำแหน่ง</p>
                  <p class="font-medium">{{ s1.position || '—' }}</p>
                </div>
                <div>
                  <p class="text-base-content/50 text-xs mb-0.5">สังกัด</p>
                  <p class="font-medium">{{ s1.department || '—' }}</p>
                </div>
                <div>
                  <p class="text-base-content/50 text-xs mb-0.5">เบอร์โทรศัพท์</p>
                  <p class="font-medium">{{ s1.phone || '—' }}</p>
                </div>
                <div>
                  <p class="text-base-content/50 text-xs mb-0.5">สถานะสมรส</p>
                  <p class="font-medium">{{ s1.marital_status === 'married' ? 'สมรส' : 'โสด' }}</p>
                </div>
                <div v-if="s1.marital_status === 'married'">
                  <p class="text-base-content/50 text-xs mb-0.5">คู่สมรส</p>
                  <p class="font-medium">{{ s1.spouse_name || '—' }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Loan Details -->
          <div class="card bg-base-100 border border-base-300">
            <div class="card-body p-5">
              <h3 class="font-bold text-sm text-base-content/60 uppercase tracking-wide mb-3">รายละเอียดเงินกู้</h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
                <div>
                  <p class="text-base-content/50 text-xs mb-0.5">ยอดเงินกู้ที่ขอ</p>
                  <p class="text-xl font-black text-primary">{{ loanAmount }}</p>
                </div>
                <div>
                  <p class="text-base-content/50 text-xs mb-0.5">ระยะเวลาผ่อน</p>
                  <p class="font-medium">{{ s2.repayment_period ? s2.repayment_period + ' งวด' : '—' }}</p>
                </div>
                <div>
                  <p class="text-base-content/50 text-xs mb-0.5">ช่องทางรับเงิน</p>
                  <p class="font-medium">{{ s2.payout_method === 'transfer' ? 'โอนเข้าบัญชี' : 'รับด้วยตนเอง' }}</p>
                </div>
                <div class="col-span-2 sm:col-span-3">
                  <p class="text-base-content/50 text-xs mb-0.5">วัตถุประสงค์</p>
                  <p class="font-medium">{{ s2.loan_purpose || '—' }}</p>
                </div>
                <div v-if="s2.payout_method === 'transfer'">
                  <p class="text-base-content/50 text-xs mb-0.5">ธนาคาร</p>
                  <p class="font-medium">{{ s2.bank_name || '—' }}</p>
                </div>
                <div v-if="s2.payout_method === 'transfer'">
                  <p class="text-base-content/50 text-xs mb-0.5">เลขบัญชี</p>
                  <p class="font-medium font-mono">{{ s2.bank_account || '—' }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Guarantors -->
          <div v-if="guarantors.length > 0" class="card bg-base-100 border border-base-300">
            <div class="card-body p-5">
              <h3 class="font-bold text-sm text-base-content/60 uppercase tracking-wide mb-3">
                ผู้ค้ำประกัน ({{ guarantors.length }} คน)
              </h3>
              <div class="space-y-4">
                <div
                  v-for="(g, i) in guarantors"
                  :key="i"
                  class="border border-base-200 rounded-lg p-3 text-sm"
                >
                  <p class="font-bold text-primary text-xs uppercase mb-2">ผู้ค้ำ {{ i + 1 }}</p>
                  <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    <div>
                      <p class="text-base-content/50 text-xs">ชื่อ-นามสกุล</p>
                      <p class="font-medium">{{ g.name || '—' }}</p>
                    </div>
                    <div>
                      <p class="text-base-content/50 text-xs">รหัสสมาชิก</p>
                      <p class="font-medium">{{ g.member_code || '—' }}</p>
                    </div>
                    <div>
                      <p class="text-base-content/50 text-xs">เลขบัตรประชาชน</p>
                      <p class="font-medium">{{ g.id_card || '—' }}</p>
                    </div>
                    <div>
                      <p class="text-base-content/50 text-xs">ตำแหน่ง</p>
                      <p class="font-medium">{{ g.position || '—' }}</p>
                    </div>
                    <div>
                      <p class="text-base-content/50 text-xs">สังกัด</p>
                      <p class="font-medium">{{ g.department || '—' }}</p>
                    </div>
                    <div>
                      <p class="text-base-content/50 text-xs">สถานะสมรส</p>
                      <p class="font-medium">{{ g.marital_status === 'married' ? 'สมรส' : 'โสด' }}</p>
                    </div>
                    <div v-if="g.marital_status === 'married'" class="col-span-2">
                      <p class="text-base-content/50 text-xs">คู่สมรส</p>
                      <p class="font-medium">{{ g.spouse_name || '—' }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- ════ RIGHT COLUMN (2/5): Documents + Decision ════ -->
        <div class="xl:col-span-2 space-y-5">

          <!-- PDF Form -->
          <div class="card bg-base-100 border border-base-300">
            <div class="card-body p-5">
              <h3 class="font-bold text-sm text-base-content/60 uppercase tracking-wide mb-3">แบบฟอร์ม PDF</h3>
              <button
                class="btn btn-outline btn-primary btn-sm gap-2 w-full"
                @click="staffService.openPdf(appId)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                ดูสัญญาเงินกู้ (PDF)
              </button>
            </div>
          </div>

          <!-- Attachments -->
          <div class="card bg-base-100 border border-base-300">
            <div class="card-body p-5">
              <h3 class="font-bold text-sm text-base-content/60 uppercase tracking-wide mb-3">
                เอกสารแนบ ({{ app.attachments.length }} ไฟล์)
              </h3>

              <div v-if="app.attachments.length === 0" class="text-sm text-base-content/40 italic">
                ไม่มีเอกสารแนบ
              </div>

              <div v-else class="space-y-2">
                <div
                  v-for="(att, i) in app.attachments"
                  :key="i"
                  class="flex items-center justify-between gap-2 py-1.5 border-b border-base-200 last:border-0"
                >
                  <div class="flex-1 min-w-0">
                    <p class="text-xs font-medium truncate">
                      {{ DOC_LABEL[att.file_type] ?? att.file_type }}
                    </p>
                    <p class="text-[10px] text-base-content/40 truncate">{{ att.original_filename }}</p>
                  </div>
                  <button
                    class="btn btn-ghost btn-xs text-primary shrink-0"
                    @click="staffService.openAttachment(att.id)"
                  >
                    ดู
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Signatures -->
          <div v-if="app.parties.length > 0" class="card bg-base-100 border border-base-300">
            <div class="card-body p-5">
              <h3 class="font-bold text-sm text-base-content/60 uppercase tracking-wide mb-3">ลายเซ็น</h3>
              <div class="space-y-2">
                <div
                  v-for="p in app.parties"
                  :key="p.role"
                  class="flex items-center justify-between text-sm"
                >
                  <span class="text-base-content/70">{{ p.full_name }}</span>
                  <span class="badge badge-xs gap-1" :class="p.has_signature ? 'badge-success' : 'badge-error'">
                    {{ p.has_signature ? '✓ ลงนามแล้ว' : '✗ ยังไม่ลงนาม' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Decision Panel -->
          <div v-if="!isFinalized" class="card bg-base-100 border-t-4 border-t-primary border border-base-300">
            <div class="card-body p-5">
              <h3 class="font-bold text-sm text-base-content/60 uppercase tracking-wide mb-4">ผลการพิจารณา</h3>
              <div class="space-y-2">
                <button
                  class="btn btn-success text-white btn-sm w-full"
                  @click="openDecisionModal('approved')"
                >
                  อนุมัติเงินกู้
                </button>
                <button
                  class="btn btn-warning btn-sm w-full"
                  @click="openDecisionModal('pending_documents')"
                >
                  ขอเอกสารเพิ่มเติม
                </button>
                <button
                  class="btn btn-error text-white btn-sm w-full"
                  @click="openDecisionModal('rejected')"
                >
                  ปฏิเสธคำขอ
                </button>
                <button
                  class="btn btn-ghost btn-sm w-full text-base-content/50"
                  @click="openDecisionModal('under_review')"
                >
                  ทำเครื่องหมายกำลังตรวจสอบ
                </button>
              </div>
            </div>
          </div>

          <!-- Finalized notice -->
          <div v-else class="alert py-3 text-sm"
            :class="app.status === 'approved' ? 'alert-success' : 'alert-error'">
            <span>{{ app.status === 'approved' ? '✓ อนุมัติเรียบร้อยแล้ว' : '✗ ปฏิเสธคำขอนี้แล้ว' }}</span>
          </div>

        </div>
      </div>
    </div>

    <!-- ════ Decision Confirm Modal ════ -->
    <dialog class="modal" :class="{ 'modal-open': showModal }">
      <div class="modal-box max-w-md">
        <h3 class="font-bold text-lg mb-4">
          ยืนยัน: {{ selectedStatus ? DECISION_LABEL[selectedStatus] : '' }}
        </h3>

        <!-- Remarks field — required for reject/pending_docs -->
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text font-medium">
              ความเห็น / หมายเหตุ
              <span v-if="remarksRequired" class="text-error ml-1">*จำเป็น</span>
            </span>
          </label>
          <textarea
            v-model="remarks"
            class="textarea textarea-bordered h-24 text-sm"
            :placeholder="
              selectedStatus === 'pending_documents'
                ? 'ระบุเอกสารที่ต้องการเพิ่มเติม เช่น สำเนาทะเบียนบ้าน ฉบับล่าสุด...'
                : selectedStatus === 'rejected'
                ? 'ระบุเหตุผลที่ปฏิเสธ...'
                : 'ความเห็นเพิ่มเติม (ไม่บังคับ)...'
            "
          ></textarea>
          <label v-if="remarksRequired && !remarks.trim()" class="label">
            <span class="label-text-alt text-error">กรุณาระบุหมายเหตุ</span>
          </label>
        </div>

        <div v-if="submitError" class="alert alert-error py-2 text-sm mb-3">{{ submitError }}</div>

        <div class="modal-action gap-2">
          <button class="btn btn-ghost" :disabled="submitting" @click="showModal = false">
            ยกเลิก
          </button>
          <button
            class="btn text-white"
            :class="selectedStatus ? DECISION_BTN_CLASS[selectedStatus] : ''"
            :disabled="!canConfirm || submitting"
            @click="confirmDecision"
          >
            <span v-if="submitting" class="loading loading-spinner loading-sm"></span>
            ยืนยัน
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="showModal = false">
        <button>close</button>
      </form>
    </dialog>

  </AppLayout>
</template>
