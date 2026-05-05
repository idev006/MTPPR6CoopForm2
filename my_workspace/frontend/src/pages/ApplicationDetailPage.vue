<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { applicationService, type ApplicationDetail } from '@/services/application.service'
import { attachmentService, type Attachment } from '@/services/attachment.service'
import { useToastStore } from '@/stores/toast.store'

const route = useRoute()
const router = useRouter()
const toast = useToastStore()

const app = ref<ApplicationDetail | null>(null)
const loading = ref(true)
const error = ref('')
const cancelling = ref(false)
const showCancelModal = ref(false)
const cancelReason = ref('')

// Upload additional docs state
const uploadedDocs = ref<Attachment[]>([])
const newFileType = ref('other')
const newFile = ref<File | null>(null)
const uploading = ref(false)
const resubmitting = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const appId = route.params.id as string

const EXTRA_DOC_TYPES = [
  { value: 'payroll',           label: 'สลิปเงินเดือน / หนังสือรับรองเงินเดือน' },
  { value: 'id_card_borrower',  label: 'สำเนาบัตรประชาชนผู้กู้' },
  { value: 'house_reg_borrower',label: 'สำเนาทะเบียนบ้านผู้กู้' },
  { value: 'id_card_spouse',    label: 'สำเนาบัตรประชาชนคู่สมรสผู้กู้' },
  { value: 'house_reg_spouse',  label: 'สำเนาทะเบียนบ้านคู่สมรสผู้กู้' },
  { value: 'marriage_cert',     label: 'สำเนาทะเบียนสมรสผู้กู้' },
  { value: 'id_card_g1',        label: 'สำเนาบัตรประชาชนผู้ค้ำ 1' },
  { value: 'house_reg_g1',      label: 'สำเนาทะเบียนบ้านผู้ค้ำ 1' },
  { value: 'id_card_g2',        label: 'สำเนาบัตรประชาชนผู้ค้ำ 2' },
  { value: 'house_reg_g2',      label: 'สำเนาทะเบียนบ้านผู้ค้ำ 2' },
  { value: 'other',             label: 'เอกสารอื่นๆ' },
]

const DOC_LABEL: Record<string, string> = Object.fromEntries(
  EXTRA_DOC_TYPES.map(d => [d.value, d.label])
)

const statusLabel: Record<string, string> = {
  draft: 'ร่าง',
  submitted: 'รออนุมัติ',
  under_review: 'กำลังพิจารณา',
  approved: 'อนุมัติแล้ว',
  rejected: 'ไม่อนุมัติ',
  cancelled: 'ยกเลิกแล้ว',
  pending_documents: 'รอเอกสารเพิ่มเติม',
}

const statusClass: Record<string, string> = {
  draft: 'badge-ghost',
  submitted: 'badge-info',
  under_review: 'badge-warning',
  approved: 'badge-success',
  rejected: 'badge-error',
  cancelled: 'badge-neutral',
  pending_documents: 'badge-warning',
}

const formTypeLabel: Record<string, string> = {
  loan_ordinary: 'กู้สามัญ',
  loan_emergency: 'กู้ฉุกเฉิน',
}

const canCancel = computed(() => app.value?.status === 'submitted')
const isPendingDocs = computed(() => app.value?.status === 'pending_documents')

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('th-TH', {
    year: 'numeric', month: 'long', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function formatAmount(amount: number | null | undefined) {
  if (amount == null) return '—'
  return amount.toLocaleString('th-TH', { style: 'currency', currency: 'THB', minimumFractionDigits: 0 })
}

function formatBytes(bytes: number | null | undefined) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

onMounted(async () => {
  try {
    app.value = await applicationService.getById(appId)
    if (app.value?.status === 'pending_documents') {
      await loadAttachments()
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'ไม่สามารถโหลดข้อมูลคำขอได้'
  } finally {
    loading.value = false
  }
})

async function loadAttachments() {
  try {
    uploadedDocs.value = await attachmentService.list(appId)
  } catch {
    // non-critical
  }
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  newFile.value = input.files?.[0] ?? null
}

async function uploadFile() {
  if (!newFile.value) return
  uploading.value = true
  try {
    await attachmentService.upload(appId, newFile.value, newFileType.value)
    toast.show('อัปโหลดเอกสารสำเร็จ')
    newFile.value = null
    if (fileInputRef.value) fileInputRef.value.value = ''
    await loadAttachments()
  } catch (err: any) {
    toast.show(err?.response?.data?.detail || 'อัปโหลดไม่สำเร็จ', 'error')
  } finally {
    uploading.value = false
  }
}

async function doResubmit() {
  resubmitting.value = true
  try {
    await applicationService.resubmit(appId)
    app.value!.status = 'submitted'
    toast.show('ส่งเอกสารเพิ่มเติมเรียบร้อยแล้ว รอเจ้าหน้าที่ตรวจสอบ')
  } catch (err: any) {
    toast.show(err?.response?.data?.detail || 'เกิดข้อผิดพลาด กรุณาลองใหม่', 'error')
  } finally {
    resubmitting.value = false
  }
}

async function confirmCancel() {
  if (!app.value) return
  cancelling.value = true
  try {
    await applicationService.cancel(appId, cancelReason.value.trim() || undefined)
    app.value.status = 'cancelled'
    app.value.cancelled_at = new Date().toISOString()
    app.value.cancel_reason = cancelReason.value.trim() || null
    showCancelModal.value = false
    cancelReason.value = ''
    toast.show('ยกเลิกคำขอเรียบร้อยแล้ว')
  } catch (err: any) {
    toast.show(err.response?.data?.detail || 'ไม่สามารถยกเลิกคำขอได้', 'error')
  } finally {
    cancelling.value = false
  }
}
</script>

<template>
  <AppLayout>
    <div class="p-6 max-w-3xl mx-auto">

      <!-- Back -->
      <button class="btn btn-ghost btn-sm gap-2 mb-6" @click="router.push({ name: 'dashboard' })">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        กลับหน้าหลัก
      </button>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-16">
        <span class="loading loading-spinner loading-lg"></span>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="alert alert-error">
        <span>{{ error }}</span>
      </div>

      <!-- Content -->
      <template v-else-if="app">

        <!-- Header card -->
        <div class="card bg-base-100 shadow-sm mb-4">
          <div class="card-body">
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p class="text-xs text-base-content/50 uppercase tracking-wider">หมายเลขคำขอ</p>
                <h1 class="text-2xl font-bold font-mono mt-0.5">{{ app.application_no }}</h1>
              </div>
              <span class="badge badge-lg" :class="statusClass[app.status] ?? 'badge-ghost'">
                {{ statusLabel[app.status] ?? app.status }}
              </span>
            </div>

            <div class="divider my-2"></div>

            <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
              <div>
                <p class="text-base-content/50">ประเภทคำขอ</p>
                <p class="font-medium">{{ formTypeLabel[app.form_type] ?? app.form_type }}</p>
              </div>
              <div>
                <p class="text-base-content/50">วงเงินที่ขอกู้</p>
                <p class="font-medium">{{ formatAmount(app.requested_amount) }}</p>
              </div>
              <div>
                <p class="text-base-content/50">จำนวนงวด</p>
                <p class="font-medium">{{ app.requested_installments ? `${app.requested_installments} งวด` : '—' }}</p>
              </div>
              <div class="col-span-2 sm:col-span-3">
                <p class="text-base-content/50">วัตถุประสงค์</p>
                <p class="font-medium">{{ app.loan_purpose || '—' }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- ════ pending_documents: upload panel ════ -->
        <div v-if="isPendingDocs" class="card border-2 border-warning bg-warning/5 mb-4">
          <div class="card-body p-5 space-y-4">

            <!-- Staff message -->
            <div class="flex gap-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-warning shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M12 3a9 9 0 110 18A9 9 0 0112 3z" />
              </svg>
              <div>
                <p class="font-bold text-warning-content">เจ้าหน้าที่ขอเอกสารเพิ่มเติม</p>
                <p v-if="app.review_remarks" class="text-sm mt-1 bg-warning/20 rounded p-2 font-medium">
                  "{{ app.review_remarks }}"
                </p>
                <p class="text-sm text-base-content/70 mt-1">
                  กรุณาอัปโหลดเอกสารที่ระบุ จากนั้นกด "ยืนยันส่งเอกสารเพิ่มเติม"
                </p>
              </div>
            </div>

            <div class="divider my-0 text-xs text-base-content/40">อัปโหลดเอกสาร</div>

            <!-- Upload form -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="form-control">
                <label class="label py-1">
                  <span class="label-text text-xs font-medium">ประเภทเอกสาร</span>
                </label>
                <select v-model="newFileType" class="select select-bordered select-sm w-full">
                  <option v-for="t in EXTRA_DOC_TYPES" :key="t.value" :value="t.value">
                    {{ t.label }}
                  </option>
                </select>
              </div>

              <div class="form-control">
                <label class="label py-1">
                  <span class="label-text text-xs font-medium">เลือกไฟล์ (PDF, JPG, PNG)</span>
                </label>
                <input
                  ref="fileInputRef"
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  class="file-input file-input-bordered file-input-sm w-full"
                  @change="onFileChange"
                />
              </div>
            </div>

            <button
              class="btn btn-outline btn-sm w-fit gap-2"
              :disabled="!newFile || uploading"
              @click="uploadFile"
            >
              <span v-if="uploading" class="loading loading-spinner loading-xs"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              {{ uploading ? 'กำลังอัปโหลด...' : 'อัปโหลด' }}
            </button>

            <!-- Uploaded files list -->
            <div v-if="uploadedDocs.length > 0" class="space-y-1">
              <p class="text-xs font-bold text-base-content/60 uppercase tracking-wide">
                เอกสารที่แนบไว้แล้ว ({{ uploadedDocs.length }} ไฟล์)
              </p>
              <div
                v-for="doc in uploadedDocs"
                :key="doc.id"
                class="flex items-center justify-between gap-2 py-1.5 px-3 bg-base-100 rounded-lg border border-base-200 text-sm"
              >
                <div class="flex items-center gap-2 min-w-0">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div class="min-w-0">
                    <p class="truncate font-medium text-xs">{{ DOC_LABEL[doc.file_type] ?? doc.file_type }}</p>
                    <p class="truncate text-[10px] text-base-content/40">{{ doc.original_filename }} · {{ formatBytes(doc.file_size_bytes) }}</p>
                  </div>
                </div>
                <button
                  class="btn btn-ghost btn-xs text-primary shrink-0"
                  @click="attachmentService.openFile(doc.id)"
                >
                  ดู
                </button>
              </div>
            </div>

            <div class="divider my-0"></div>

            <!-- Resubmit button -->
            <div class="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <button
                class="btn btn-warning gap-2"
                :disabled="resubmitting || uploadedDocs.length === 0"
                @click="doResubmit"
              >
                <span v-if="resubmitting" class="loading loading-spinner loading-sm"></span>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
                ยืนยันส่งเอกสารเพิ่มเติม
              </button>
              <p v-if="uploadedDocs.length === 0" class="text-xs text-base-content/50">
                กรุณาอัปโหลดเอกสารอย่างน้อย 1 ไฟล์ก่อนยืนยัน
              </p>
            </div>

          </div>
        </div>

        <!-- Timeline card -->
        <div class="card bg-base-100 shadow-sm mb-4">
          <div class="card-body">
            <h2 class="font-semibold text-sm uppercase tracking-wider text-base-content/50 mb-3">ประวัติการดำเนินการ</h2>
            <ul class="timeline timeline-vertical timeline-compact text-sm">
              <li>
                <div class="timeline-start timeline-box">ยื่นคำขอ</div>
                <div class="timeline-middle">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-5 w-5 text-primary">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="timeline-end text-base-content/60">{{ formatDate(app.submitted_at ?? app.created_at) }}</div>
                <hr />
              </li>
              <li>
                <hr />
                <div class="timeline-start timeline-box"
                  :class="{ 'opacity-40': !['under_review','approved','rejected','pending_documents'].includes(app.status) }">
                  กำลังพิจารณา
                </div>
                <div class="timeline-middle">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-5 w-5"
                    :class="['under_review','approved','rejected','pending_documents'].includes(app.status) ? 'text-primary' : 'text-base-content/20'">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="timeline-end text-base-content/60">
                  {{ ['under_review','approved','rejected','pending_documents'].includes(app.status) ? formatDate(app.reviewed_at) : '' }}
                </div>
                <hr />
              </li>
              <li v-if="app.status === 'pending_documents'">
                <hr />
                <div class="timeline-start timeline-box bg-warning text-warning-content">รอเอกสารเพิ่ม</div>
                <div class="timeline-middle">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-5 w-5 text-warning">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="timeline-end text-base-content/60">{{ formatDate(app.reviewed_at) }}</div>
              </li>
              <li v-else>
                <hr />
                <div class="timeline-start timeline-box" :class="{ 'opacity-40': !['approved','rejected'].includes(app.status) }">
                  {{ app.status === 'rejected' ? 'ไม่อนุมัติ' : 'อนุมัติ' }}
                </div>
                <div class="timeline-middle">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-5 w-5"
                    :class="app.status === 'approved' ? 'text-success' : app.status === 'rejected' ? 'text-error' : 'text-base-content/20'">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="timeline-end text-base-content/60">
                  {{ ['approved','rejected'].includes(app.status) ? formatDate(app.reviewed_at) : '' }}
                </div>
              </li>
            </ul>

            <!-- remarks (approved/rejected only — pending_docs shows above) -->
            <div v-if="app.review_remarks && !isPendingDocs" class="mt-3 p-3 bg-base-200 rounded-lg text-sm">
              <p class="text-base-content/50 text-xs mb-1">หมายเหตุจากเจ้าหน้าที่</p>
              <p>{{ app.review_remarks }}</p>
            </div>

            <!-- เหตุผลการยกเลิก -->
            <div v-if="app.status === 'cancelled'" class="mt-3 p-3 bg-error/10 border border-error/20 rounded-lg text-sm">
              <p class="text-error text-xs font-medium mb-1">🚫 ยกเลิกเมื่อ {{ formatDate(app.cancelled_at) }}</p>
              <p v-if="app.cancel_reason" class="text-base-content/70">{{ app.cancel_reason }}</p>
              <p v-else class="text-base-content/40 italic">ไม่ได้ระบุเหตุผล</p>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex flex-wrap gap-3">
          <a
            v-if="app.has_pdf"
            :href="`/api/v1/pdf/${app.id}/download`"
            target="_blank"
            class="btn btn-primary btn-sm gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            ดาวน์โหลด PDF
          </a>

          <button
            v-if="canCancel"
            class="btn btn-error btn-outline btn-sm gap-2"
            @click="showCancelModal = true"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            ยกเลิกคำขอ
          </button>
        </div>

      </template>
    </div>

    <!-- Cancel confirm modal -->
    <dialog class="modal" :class="{ 'modal-open': showCancelModal }">
      <div class="modal-box">
        <h3 class="font-bold text-lg">ยืนยันการยกเลิกคำขอ</h3>
        <p class="py-3 text-base-content/70 text-sm">
          ยกเลิกคำขอหมายเลข <span class="font-mono font-bold">{{ app?.application_no }}</span><br />
          <span class="text-error text-xs">การดำเนินการนี้ไม่สามารถเปลี่ยนกลับได้</span>
        </p>

        <!-- เหตุผลการยกเลิก (optional) -->
        <div class="form-control">
          <label class="label pb-1">
            <span class="label-text text-sm">เหตุผลการยกเลิก <span class="text-base-content/40">(ไม่บังคับ)</span></span>
            <span class="label-text-alt text-xs text-base-content/40">{{ cancelReason.length }}/500</span>
          </label>
          <textarea
            v-model="cancelReason"
            class="textarea textarea-bordered resize-none text-sm"
            rows="3"
            maxlength="500"
            placeholder="เช่น เปลี่ยนใจ, ได้รับการช่วยเหลือจากที่อื่น..."
            :disabled="cancelling"
          ></textarea>
        </div>

        <div class="modal-action">
          <button class="btn btn-ghost" @click="showCancelModal = false; cancelReason = ''" :disabled="cancelling">ปิด</button>
          <button class="btn btn-error" @click="confirmCancel" :disabled="cancelling">
            <span v-if="cancelling" class="loading loading-spinner loading-xs"></span>
            ยืนยันยกเลิก
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button @click="showCancelModal = false; cancelReason = ''">close</button>
      </form>
    </dialog>
  </AppLayout>
</template>
