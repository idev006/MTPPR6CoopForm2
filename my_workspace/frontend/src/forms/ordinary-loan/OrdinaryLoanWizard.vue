<script setup lang="ts">
import { computed, ref } from 'vue'
import { useFormStore } from '@/stores/form.store'
import { useAuthStore } from '@/stores/auth.store'
import { ROLES } from '@/constants/roles'
import { attachmentService, type Attachment } from '@/services/attachment.service'
import api from '@/services/api.service'

import BaseWizardLayout from '@/forms/shared/BaseWizardLayout.vue'
import Step1PersonalInfo from '@/forms/shared/Step1PersonalInfo.vue'
import Step2LoanDetails from './Step2LoanDetails.vue'
import Step3Guarantors from './Step3Guarantors.vue'
import StepAttachments from '@/forms/shared/StepAttachments.vue'
import Step4SignatureHub from '@/forms/shared/Step4SignatureHub.vue'
import Step5StaffVerification from '@/forms/staff/Step5StaffVerification.vue'
import Step6ContractFinalization from '@/forms/staff/Step6ContractFinalization.vue'
import StepReview from './StepReview.vue'

import type { Step1Data, Step2Data, Step3Data, Step4Data, Step5Data, Step6Data } from '@/types/form'

const auth = useAuthStore()
const form = useFormStore()

const ALL_TABS = [
  { label: 'ข้อมูลผู้กู้', component: Step1PersonalInfo, roles: [ROLES.BORROWER, ROLES.STAFF] },
  { label: 'รายละเอียดเงินกู้', component: Step2LoanDetails, roles: [ROLES.BORROWER, ROLES.STAFF] },
  { label: 'ผู้ค้ำประกัน', component: Step3Guarantors, roles: [ROLES.BORROWER, ROLES.STAFF] },
  { label: 'เอกสารประกอบ', component: StepAttachments, roles: [ROLES.BORROWER, ROLES.STAFF] },
  { label: 'ลงนาม', component: Step4SignatureHub, roles: [ROLES.BORROWER, ROLES.STAFF] },
  { label: 'ตรวจสอบข้อมูล', component: StepReview, roles: [ROLES.BORROWER] },
  { label: 'ตรวจสอบ (Staff)', component: Step5StaffVerification, roles: [ROLES.STAFF] },
  { label: 'สัญญา (Staff)', component: Step6ContractFinalization, roles: [ROLES.STAFF] },
]

const tabs = computed(() => ALL_TABS.filter(t => auth.hasRole(t.roles)))

const safeTabIndex = computed(() =>
  Math.min(Math.max(form.currentTab, 0), tabs.value.length - 1)
)

const currentTabDef = computed(() => tabs.value[safeTabIndex.value])

const currentStepData = computed(() => {
  const comp = currentTabDef.value?.component
  if (!comp) return null
  if (comp === Step1PersonalInfo) return form.step1
  if (comp === Step2LoanDetails) return form.step2
  if (comp === Step3Guarantors) return form.step3
  if (comp === Step4SignatureHub) return form.step4
  if (comp === StepReview) return null
  if (comp === Step5StaffVerification) return form.step5
  if (comp === Step6ContractFinalization) return form.step6
  return null
})

function handleUpdate(value: any) {
  const comp = currentTabDef.value?.component
  if (!comp) return
  if (comp === Step1PersonalInfo) form.updateStep1(value as Step1Data)
  else if (comp === Step2LoanDetails) form.updateStep2(value as Step2Data)
  else if (comp === Step3Guarantors) form.updateStep3(value as Step3Data)
  else if (comp === Step4SignatureHub) form.updateStep4(value as Step4Data)
  else if (comp === Step5StaffVerification) form.updateStep5(value as Step5Data)
  else if (comp === Step6ContractFinalization) form.updateStep6(value as Step6Data)
}

const lastSavedText = computed(() => {
  if (!form.lastSaved) return ''
  return `บันทึกอัตโนมัติ ${form.lastSaved.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })}`
})

// ─── Confirm Modal ────────────────────────────────────────────
const showConfirm = ref(false)
const confirmAttachments = ref<Attachment[]>([])
const loadingConfirm = ref(false)

const DOC_LABEL: Record<string, string> = {
  payroll:            'บัญชีเงินเดือน',
  id_card_borrower:   'สำเนาบัตรประชาชนผู้กู้ (4 ชุด)',
  house_reg_borrower: 'สำเนาทะเบียนบ้านผู้กู้ (2 ชุด)',
  id_card_spouse:     'สำเนาบัตรประชาชนคู่สมรส (ผู้กู้)',
  house_reg_spouse:   'สำเนาทะเบียนบ้านคู่สมรส (ผู้กู้)',
  marriage_cert:      'สำเนาทะเบียนสมรส (ผู้กู้)',
  id_card_g1:         'สำเนาบัตรประชาชนผู้ค้ำฯ คนที่ 1',
  house_reg_g1:       'สำเนาทะเบียนบ้านผู้ค้ำฯ คนที่ 1',
  id_card_g2:         'สำเนาบัตรประชาชนผู้ค้ำฯ คนที่ 2',
  house_reg_g2:       'สำเนาทะเบียนบ้านผู้ค้ำฯ คนที่ 2',
}

const ATTACHMENT_TYPE_LABEL: Record<string, string> = {
  payroll:              'บัญชีเงินเดือน',
  id_card_borrower:     'บัตรประชาชน/ข้าราชการ (ผู้กู้)',
  house_reg_borrower:   'ทะเบียนบ้าน (ผู้กู้)',
  id_card_spouse:       'บัตรประชาชนคู่สมรส (ผู้กู้)',
  house_reg_spouse:     'ทะเบียนบ้านคู่สมรส (ผู้กู้)',
  marriage_cert:        'ทะเบียนสมรส (ผู้กู้)',
  id_card_g1:           'บัตรประชาชน/ข้าราชการ (ผู้ค้ำฯ 1)',
  house_reg_g1:         'ทะเบียนบ้าน (ผู้ค้ำฯ 1)',
  id_card_spouse_g1:    'บัตรประชาชนคู่สมรส (ผู้ค้ำฯ 1)',
  house_reg_spouse_g1:  'ทะเบียนบ้านคู่สมรส (ผู้ค้ำฯ 1)',
  marriage_cert_g1:     'ทะเบียนสมรส (ผู้ค้ำฯ 1)',
  id_card_g2:           'บัตรประชาชน/ข้าราชการ (ผู้ค้ำฯ 2)',
  house_reg_g2:         'ทะเบียนบ้าน (ผู้ค้ำฯ 2)',
  id_card_spouse_g2:    'บัตรประชาชนคู่สมรส (ผู้ค้ำฯ 2)',
  house_reg_spouse_g2:  'ทะเบียนบ้านคู่สมรส (ผู้ค้ำฯ 2)',
  marriage_cert_g2:     'ทะเบียนสมรส (ผู้ค้ำฯ 2)',
  name_change:          'ใบเปลี่ยนชื่อ-สกุล / ใบหย่า',
  other:                'เอกสารอื่นๆ',
}

const requiredDocKeys = computed(() => {
  const keys = ['payroll', 'id_card_borrower', 'house_reg_borrower']

  // borrower spouse docs — required when married
  if (form.step1.marital_status === 'married') {
    keys.push('id_card_spouse', 'house_reg_spouse', 'marriage_cert')
  }

  // ต้องมีผู้ค้ำ 2 คนเสมอ
  keys.push('id_card_g1', 'house_reg_g1', 'id_card_g2', 'house_reg_g2')

  // guarantor spouse docs — required ถ้าผู้ค้ำสมรส
  const g = form.step3.guarantors
  if (g[0]?.marital_status === 'married') keys.push('id_card_spouse_g1', 'house_reg_spouse_g1', 'marriage_cert_g1')
  if (g[1]?.marital_status === 'married') keys.push('id_card_spouse_g2', 'house_reg_spouse_g2', 'marriage_cert_g2')

  return keys
})

const uploadedKeys = computed(() => new Set(confirmAttachments.value.map(a => a.file_type)))

const missingRequired = computed(() =>
  requiredDocKeys.value.filter(k => !uploadedKeys.value.has(k))
)

const REQUIRED_GUARANTORS = 2
const guarantorCount = REQUIRED_GUARANTORS

const allGuarantorsSigned = computed(() =>
  form.step4.guarantor_sigs
    .slice(0, REQUIRED_GUARANTORS)
    .every(s => s?.signed)
)

const canSubmit = computed(() =>
  form.pdfViewed &&
  !!form.step4.borrower_sig?.signed &&
  allGuarantorsSigned.value &&
  missingRequired.value.length === 0
)

async function openConfirm() {
  showConfirm.value = true
  loadingConfirm.value = true
  try {
    if (form.draftId) {
      confirmAttachments.value = await attachmentService.list(form.draftId)
    }
  } finally {
    loadingConfirm.value = false
  }
}

function goToReviewTab() {
  const idx = tabs.value.findIndex(t => t.component === StepReview)
  if (idx !== -1) form.setTab(idx)
  showConfirm.value = false
}

async function openPreviewFromModal() {
  try {
    const res = await api.get('/applications/preview/download', { responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
    window.open(url, '_blank')
    form.setPdfViewed()
  } catch { /* silent */ }
}

async function doSubmit() {
  const ok = await form.submitForm()
  if (ok) showConfirm.value = false
}

function formatSize(bytes: number) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<template>
  <BaseWizardLayout
    :tabs="tabs"
    :current-tab="safeTabIndex"
    :saving="form.saving"
    :save-error="form.saveError"
    :last-saved-text="lastSavedText"
    :is-dirty="form.isDirty"
    :submitting="form.submitting"
    :submit-error="form.submitError"
    :can-submit="auth.hasRole(ROLES.BORROWER)"
    @set-tab="form.setTab"
    @save="form.save"
    @submit="openConfirm"
    @prev="form.setTab(form.currentTab - 1)"
    @next="form.setTab(form.currentTab + 1)"
  >
    <component
      :is="currentTabDef.component"
      :model-value="currentStepData"
      @update:model-value="handleUpdate"
    />
  </BaseWizardLayout>

  <!-- ─── Confirm Submit Modal ─────────────────────────────────── -->
  <div v-if="showConfirm" class="modal modal-open">
    <div class="modal-box max-w-lg w-full flex flex-col gap-0 p-0 overflow-hidden">

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-base-300">
        <h3 class="font-bold text-lg">ยืนยันการส่งคำขอกู้เงินสามัญ</h3>
        <button class="btn btn-ghost btn-sm btn-circle" :disabled="form.submitting" @click="showConfirm = false">✕</button>
      </div>

      <!-- Scrollable body -->
      <div class="overflow-y-auto max-h-[65vh] px-6 py-4 space-y-5">

        <!-- Warning banner -->
        <div class="alert alert-warning py-3 text-sm gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
          </svg>
          <span>เมื่อส่งแล้ว <strong>ไม่สามารถแก้ไขข้อมูลได้อีก</strong> กรุณาตรวจสอบให้ครบถ้วนก่อนยืนยัน</span>
        </div>

        <!-- Section: PDF Preview -->
        <section class="space-y-2">
          <p class="text-xs font-bold uppercase tracking-widest text-base-content/50">ตรวจสอบแบบฟอร์ม PDF</p>
          <div class="flex items-center justify-between p-3 rounded-lg"
            :class="form.pdfViewed ? 'bg-success/10' : 'bg-error/10'">
            <div class="flex items-center gap-2 text-sm">
              <span :class="form.pdfViewed ? 'text-success' : 'text-error'" class="text-base font-bold">
                {{ form.pdfViewed ? '✓' : '✗' }}
              </span>
              <span :class="form.pdfViewed ? 'text-success font-medium' : 'text-error font-medium'">
                {{ form.pdfViewed ? 'ดูตัวอย่างแบบฟอร์ม PDF แล้ว' : 'ยังไม่ได้ดูตัวอย่างแบบฟอร์ม PDF' }}
              </span>
            </div>
            <div class="flex gap-2">
              <button v-if="!form.pdfViewed" class="btn btn-xs btn-error btn-outline" @click="goToReviewTab">
                กลับไปดู PDF
              </button>
              <button v-else class="btn btn-xs btn-ghost text-base-content/50" @click="openPreviewFromModal">
                ดูอีกครั้ง ↗
              </button>
            </div>
          </div>
          <p v-if="!form.pdfViewed" class="text-xs text-error/80 pl-1">
            กรุณาดูตัวอย่าง PDF ก่อนส่งคำขอ เพื่อตรวจสอบความถูกต้องของข้อมูลในเอกสาร
          </p>
        </section>

        <!-- Section: Signatures -->
        <section class="space-y-2">
          <p class="text-xs font-bold uppercase tracking-widest text-base-content/50">ลายเซ็น</p>
          <div class="grid grid-cols-2 gap-2">
            <!-- Borrower -->
            <div class="flex items-center gap-2 p-2 rounded-lg text-sm"
              :class="form.step4.borrower_sig?.signed ? 'bg-success/10' : 'bg-error/10'">
              <span :class="form.step4.borrower_sig?.signed ? 'text-success' : 'text-error'" class="font-bold">
                {{ form.step4.borrower_sig?.signed ? '✓' : '✗' }}
              </span>
              <span :class="form.step4.borrower_sig?.signed ? 'text-success' : 'text-error font-medium'">ผู้กู้</span>
            </div>
            <!-- Superior (optional) -->
            <div class="flex items-center gap-2 p-2 rounded-lg text-sm bg-base-200">
              <span class="text-base-content/40 font-bold">{{ form.step4.superior_sig?.signed ? '✓' : '–' }}</span>
              <span class="text-base-content/60">ผู้บังคับบัญชา</span>
              <span class="text-xs text-base-content/40">(ไม่บังคับ)</span>
            </div>
            <!-- Guarantors -->
            <div
              v-for="(sig, i) in form.step4.guarantor_sigs.slice(0, guarantorCount)"
              :key="i"
              class="flex items-center gap-2 p-2 rounded-lg text-sm"
              :class="sig?.signed ? 'bg-success/10' : 'bg-error/10'"
            >
              <span :class="sig?.signed ? 'text-success' : 'text-error'" class="font-bold">
                {{ sig?.signed ? '✓' : '✗' }}
              </span>
              <span :class="sig?.signed ? 'text-success' : 'text-error font-medium'">ผู้ค้ำฯ {{ i + 1 }}</span>
            </div>
          </div>
        </section>

        <!-- Section: Attachments -->
        <section class="space-y-3">
          <p class="text-xs font-bold uppercase tracking-widest text-base-content/50">เอกสารแนบ</p>

          <!-- Required checklist -->
          <div class="space-y-1">
            <div
              v-for="key in requiredDocKeys"
              :key="key"
              class="flex items-center gap-2 p-2 rounded-lg text-sm"
              :class="uploadedKeys.has(key) ? 'bg-success/10' : 'bg-error/10'"
            >
              <span :class="uploadedKeys.has(key) ? 'text-success' : 'text-error'" class="font-bold w-4 text-center">
                {{ uploadedKeys.has(key) ? '✓' : '✗' }}
              </span>
              <span :class="uploadedKeys.has(key) ? 'text-success' : 'text-error font-medium'">
                {{ DOC_LABEL[key] }}
              </span>
              <span class="text-xs text-base-content/40 ml-auto">(จำเป็น)</span>
            </div>
          </div>

          <!-- Uploaded files with view button -->
          <div v-if="loadingConfirm" class="flex items-center gap-2 text-sm text-base-content/50 py-2">
            <span class="loading loading-spinner loading-xs"></span> กำลังโหลดรายการเอกสาร...
          </div>
          <div v-else-if="confirmAttachments.length > 0" class="space-y-1">
            <p class="text-xs text-base-content/50 mb-1">ไฟล์ที่อัปโหลดแล้ว (กดดูเพื่อตรวจสอบ)</p>
            <div
              v-for="att in confirmAttachments"
              :key="att.id"
              class="flex items-center justify-between p-2 rounded-lg bg-base-200 text-sm"
            >
              <div class="flex items-center gap-2 min-w-0">
                <span class="text-xs font-bold text-primary bg-primary/10 px-1.5 py-0.5 rounded">PDF</span>
                <div class="min-w-0">
                  <p class="font-medium truncate max-w-[180px]">{{ att.original_filename }}</p>
                  <p class="text-xs text-base-content/40">
                    {{ ATTACHMENT_TYPE_LABEL[att.file_type] ?? att.file_type }} · {{ formatSize(att.file_size_bytes) }}
                  </p>
                </div>
              </div>
              <button
                class="btn btn-xs btn-ghost text-primary shrink-0"
                @click="attachmentService.openFile(att.id)"
              >
                ดูไฟล์ ↗
              </button>
            </div>
          </div>
          <div v-else-if="!loadingConfirm" class="text-sm text-base-content/40 italic py-1">
            ยังไม่มีไฟล์อัปโหลด
          </div>
        </section>

        <!-- Section: Key figures -->
        <section class="space-y-2">
          <p class="text-xs font-bold uppercase tracking-widest text-base-content/50">ข้อมูลสำคัญ</p>
          <div class="grid grid-cols-3 gap-3">
            <div class="bg-base-200 rounded-lg p-3 text-center">
              <p class="text-xs text-base-content/50 mb-1">ยอดเงินกู้</p>
              <p class="font-bold text-primary text-sm">
                {{ form.step2.loan_amount ? Number(form.step2.loan_amount).toLocaleString('th-TH') + ' ฿' : '—' }}
              </p>
            </div>
            <div class="bg-base-200 rounded-lg p-3 text-center">
              <p class="text-xs text-base-content/50 mb-1">ระยะเวลา</p>
              <p class="font-bold text-sm">{{ form.step2.repayment_period ? form.step2.repayment_period + ' งวด' : '—' }}</p>
            </div>
            <div class="bg-base-200 rounded-lg p-3 text-center">
              <p class="text-xs text-base-content/50 mb-1">ผู้ค้ำประกัน</p>
              <p class="font-bold text-sm">{{ guarantorCount }} คน</p>
            </div>
          </div>
        </section>

        <!-- Blocking summary (if any issues) -->
        <div v-if="!canSubmit" class="rounded-lg border border-error/40 bg-error/5 p-3 space-y-1">
          <p class="text-xs font-bold text-error uppercase tracking-wide mb-2">ยังไม่สามารถส่งได้ — กรุณาดำเนินการ</p>
          <p v-if="!form.pdfViewed" class="text-xs text-error flex items-center gap-1">
            <span class="font-bold">✗</span> ดูตัวอย่าง PDF ก่อนส่ง
          </p>
          <p v-if="!form.step4.borrower_sig?.signed" class="text-xs text-error flex items-center gap-1">
            <span class="font-bold">✗</span> ผู้กู้ยังไม่ได้ลงนาม
          </p>
          <p v-if="!allGuarantorsSigned" class="text-xs text-error flex items-center gap-1">
            <span class="font-bold">✗</span> ผู้ค้ำประกันบางรายยังไม่ได้ลงนาม
          </p>
          <p v-if="missingRequired.length > 0" class="text-xs text-error flex items-center gap-1">
            <span class="font-bold">✗</span> เอกสารแนบจำเป็นยังไม่ครบ ({{ missingRequired.map(k => DOC_LABEL[k]).join(', ') }})
          </p>
        </div>

      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between px-6 py-4 border-t border-base-300 gap-3">
        <button class="btn btn-ghost btn-sm" :disabled="form.submitting" @click="showConfirm = false">
          ← กลับแก้ไข
        </button>
        <button
          class="btn btn-primary btn-sm gap-2"
          :disabled="!canSubmit || form.submitting"
          @click="doSubmit"
        >
          <span v-if="form.submitting" class="loading loading-spinner loading-xs"></span>
          {{ form.submitting ? 'กำลังส่ง...' : 'ยืนยัน ส่งคำขอ' }}
        </button>
      </div>

    </div>
  </div>
</template>
