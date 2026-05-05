<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFormStore } from '@/stores/form.store'
import { previewService } from '@/services/preview.service'
import api from '@/services/api.service'

const form = useFormStore()

// ── Computed summaries ─────────────────────────────────
const fullName = computed(() => {
  const s1 = form.step1
  return `${s1.title}${s1.first_name} ${s1.last_name}`.trim()
})

const loanAmount = computed(() =>
  form.step2.loan_amount
    ? Number(form.step2.loan_amount).toLocaleString('th-TH') + ' บาท'
    : '—'
)

const repaymentPeriod = computed(() =>
  form.step2.repayment_period ? `${form.step2.repayment_period} งวด` : '—'
)

const loanPurpose = computed(() => form.step2.loan_purpose || '—')

const guarantorCount = 2

const borrowerSigned = computed(() => form.step4.borrower_sig?.signed ?? false)
const superiorSigned = computed(() => form.step4.superior_sig?.signed ?? false)

// ── Preview state ──────────────────────────────────────
type PreviewState = 'idle' | 'generating' | 'ready' | 'error'
const previewState = ref<PreviewState>('idle')
const previewError = ref('')
let blobUrl = ''  // เก็บ object URL เพื่อ revoke ทีหลัง

// ตรวจสอบตอน mount — ถ้าเคยสร้าง preview ไว้แล้ว ให้แสดงปุ่มดู PDF ทันที
onMounted(async () => {
  try {
    const res = await api.get<{ exists: boolean }>('/applications/preview/exists')
    if (res.data.exists) previewState.value = 'ready'
  } catch {
    // ไม่ตอบสนอง — คง state เป็น idle
  }
})

async function generatePreview() {
  previewState.value = 'generating'
  previewError.value = ''
  // ล้าง blob URL เก่า
  if (blobUrl) { URL.revokeObjectURL(blobUrl); blobUrl = '' }
  try {
    await previewService.generate(form.formData as any)
    previewState.value = 'ready'
  } catch (err: any) {
    previewError.value = err?.response?.data?.detail || 'ไม่สามารถสร้าง PDF ได้ กรุณาลองใหม่'
    previewState.value = 'error'
  }
}

async function openPdf() {
  try {
    // ดึงไฟล์ผ่าน axios เพื่อให้ส่ง Authorization header ไปด้วย
    const res = await api.get('/applications/preview/download', { responseType: 'blob' })
    if (blobUrl) URL.revokeObjectURL(blobUrl)
    blobUrl = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
    window.open(blobUrl, '_blank')
    form.setPdfViewed()
  } catch (err: any) {
    previewError.value = err?.response?.data?.detail || 'ไม่สามารถเปิดไฟล์ PDF ได้'
    previewState.value = 'error'
  }
}
</script>

<template>
  <div class="space-y-6">

    <!-- Header -->
    <div>
      <h2 class="text-xl font-semibold text-base-content">ตรวจสอบข้อมูลก่อนส่งคำขอ</h2>
      <p class="text-sm text-base-content/60 mt-1">
        กรุณาตรวจสอบข้อมูลด้านล่างให้ถูกต้อง สามารถกดดูตัวอย่าง PDF ได้ก่อนยืนยัน
      </p>
    </div>

    <!-- Summary Card -->
    <div class="card bg-base-200 border border-base-300">
      <div class="card-body p-5 space-y-3">
        <h3 class="font-medium text-base-content/80 text-sm uppercase tracking-wide">
          สรุปข้อมูลการยื่นขอกู้เงินสามัญ
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 text-sm">
          <div class="flex justify-between border-b border-base-300 pb-1">
            <span class="text-base-content/60">ชื่อ-นามสกุล</span>
            <span class="font-medium">{{ fullName || '—' }}</span>
          </div>
          <div class="flex justify-between border-b border-base-300 pb-1">
            <span class="text-base-content/60">รหัสสมาชิก</span>
            <span class="font-medium">{{ form.step1.member_code || '—' }}</span>
          </div>
          <div class="flex justify-between border-b border-base-300 pb-1">
            <span class="text-base-content/60">ยอดเงินกู้</span>
            <span class="font-medium text-primary">{{ loanAmount }}</span>
          </div>
          <div class="flex justify-between border-b border-base-300 pb-1">
            <span class="text-base-content/60">ระยะเวลาผ่อน</span>
            <span class="font-medium">{{ repaymentPeriod }}</span>
          </div>
          <div class="flex justify-between border-b border-base-300 pb-1 md:col-span-2">
            <span class="text-base-content/60">วัตถุประสงค์</span>
            <span class="font-medium text-right max-w-xs truncate">{{ loanPurpose }}</span>
          </div>
          <div class="flex justify-between border-b border-base-300 pb-1">
            <span class="text-base-content/60">ผู้ค้ำประกัน</span>
            <span class="font-medium">{{ guarantorCount }} คน</span>
          </div>
          <div class="flex justify-between border-b border-base-300 pb-1">
            <span class="text-base-content/60">ช่องทางรับเงิน</span>
            <span class="font-medium">{{ form.step2.payout_method === 'transfer' ? 'โอนเข้าบัญชี' : 'รับด้วยตนเอง' }}</span>
          </div>
        </div>

        <!-- Signature Status -->
        <div class="pt-1">
          <p class="text-xs text-base-content/50 uppercase tracking-wide mb-2">สถานะลายเซ็น</p>
          <div class="flex flex-wrap gap-2">
            <div class="badge gap-1" :class="borrowerSigned ? 'badge-success' : 'badge-error'">
              <span>{{ borrowerSigned ? '✓' : '✗' }}</span>
              ผู้กู้
            </div>
            <div class="badge gap-1" :class="superiorSigned ? 'badge-success' : 'badge-warning'">
              <span>{{ superiorSigned ? '✓' : '–' }}</span>
              ผู้บังคับบัญชา
            </div>
            <div
              v-for="(sig, i) in form.step4.guarantor_sigs"
              :key="i"
              class="badge gap-1"
              :class="sig?.signed ? 'badge-success' : 'badge-error'"
            >
              <span>{{ sig?.signed ? '✓' : '✗' }}</span>
              ผู้ค้ำ {{ i + 1 }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- PDF Preview Section -->
    <div class="card bg-base-100 border border-base-300">
      <div class="card-body p-5">
        <h3 class="font-medium text-base-content/80 text-sm uppercase tracking-wide mb-3">
          ตรวจสอบแบบฟอร์ม PDF
        </h3>

        <p class="text-sm text-base-content/60 mb-4">
          กดปุ่มด้านล่างเพื่อให้ระบบเขียนข้อมูลลงในแบบฟอร์มขอกู้เงินสามัญ
          แล้วเปิดดู PDF เพื่อตรวจสอบความถูกต้องก่อนส่ง
        </p>

        <!-- idle / error -->
        <div v-if="previewState === 'idle' || previewState === 'error'" class="flex flex-col gap-3">
          <div v-if="previewState === 'error'" class="alert alert-error py-2 text-sm">
            {{ previewError }}
          </div>
          <button
            class="btn btn-outline btn-primary w-fit gap-2"
            @click="generatePreview"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            สร้างตัวอย่าง PDF
          </button>
        </div>

        <!-- generating -->
        <div v-else-if="previewState === 'generating'" class="flex items-center gap-3 text-sm text-base-content/60">
          <span class="loading loading-spinner loading-sm"></span>
          กำลังสร้าง PDF ตัวอย่าง...
        </div>

        <!-- ready -->
        <div v-else-if="previewState === 'ready'" class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2 text-success text-sm font-medium">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            PDF พร้อมแล้ว
          </div>

          <button class="btn btn-primary btn-sm gap-2" @click="openPdf">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            ดูไฟล์ PDF
          </button>

          <button class="btn btn-ghost btn-sm text-base-content/50" @click="generatePreview">
            สร้างใหม่
          </button>
        </div>

      </div>
    </div>

    <!-- Submit reminder -->
    <div class="alert alert-info py-3 text-sm">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-5 h-5">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      เมื่อตรวจสอบข้อมูลครบถ้วนแล้ว กดปุ่ม <strong class="mx-1">"ส่งคำขอรับพิจารณา"</strong> ด้านล่างเพื่อส่งให้เจ้าหน้าที่
    </div>

  </div>
</template>
