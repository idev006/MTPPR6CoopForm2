<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useFormStore } from '@/stores/form.store'
import { useSystemStore } from '@/stores/system.store'
import { useToastStore } from '@/stores/toast.store'
import { attachmentService } from '@/services/attachment.service'
import type { Attachment } from '@/services/attachment.service'

defineProps<{ modelValue?: any }>()

const form = useFormStore()
const system = useSystemStore()
const toast = useToastStore()
const attachments = ref<Attachment[]>([])
const uploading = ref(false)
const selectedType = ref('payroll')
const showGuide = ref(false)
const confirmDeleteId = ref<string | null>(null)
const deleting = ref(false)

// ─── รายการเอกสาร 18 รายการ ตามระเบียบสหกรณ์ฯ ──────────────────
interface DocItem {
  seq: number
  key: string
  label: string
  note?: string
  req?: boolean
  system?: boolean   // ระบบสร้างให้อัตโนมัติ (ไม่ต้องอัปโหลด)
}
interface DocGroup { group: string; items: DocItem[] }

const docRequirements: DocGroup[] = [
  {
    group: 'ผู้กู้',
    items: [
      { seq: 1,  key: 'loan_form',         label: 'คำขอกู้ฯ / สัญญากู้ / สัญญาค้ำประกันคนที่ 1-2 / หนังสืออินยอม', note: '4 ฉบับ', req: true, system: true },
      { seq: 2,  key: 'payroll',            label: 'บัญชีเงินเดือน', req: true },
      { seq: 3,  key: 'id_card_borrower',   label: 'สำเนาบัตรประจำตัวประชาชน/ข้าราชการ', note: '4 ชุด', req: true },
      { seq: 4,  key: 'house_reg_borrower', label: 'สำเนาทะเบียนบ้าน', note: '2 ชุด', req: true },
      // spouse docs — req เฉพาะเมื่อผู้กู้สมรส (ตรวจสอบผ่าน isEffectivelyRequired)
      { seq: 5,  key: 'id_card_spouse',     label: 'สำเนาบัตรประจำตัวประชาชน/ข้าราชการของคู่สมรส' },
      { seq: 6,  key: 'house_reg_spouse',   label: 'สำเนาทะเบียนบ้านของคู่สมรส' },
      { seq: 7,  key: 'marriage_cert',      label: 'สำเนาทะเบียนสมรส' },
    ],
  },
  {
    group: 'ผู้ค้ำประกัน คนที่ 1',
    items: [
      { seq: 8,  key: 'id_card_g1',         label: 'สำเนาบัตรประจำตัวประชาชน/ข้าราชการ', req: true },
      { seq: 9,  key: 'house_reg_g1',        label: 'สำเนาทะเบียนบ้าน', req: true },
      // spouse docs — req เฉพาะเมื่อผู้ค้ำสมรส (optional ถ้าไม่ทราบสถานะ)
      { seq: 12, key: 'id_card_spouse_g1',   label: 'สำเนาบัตรประชาชน/ข้าราชการของคู่สมรส' },
      { seq: 13, key: 'house_reg_spouse_g1', label: 'สำเนาทะเบียนบ้านของคู่สมรส' },
      { seq: 14, key: 'marriage_cert_g1',    label: 'สำเนาทะเบียนสมรส' },
    ],
  },
  {
    group: 'ผู้ค้ำประกัน คนที่ 2',
    items: [
      { seq: 10, key: 'id_card_g2',         label: 'สำเนาบัตรประจำตัวประชาชน/ข้าราชการ', req: true },
      { seq: 11, key: 'house_reg_g2',        label: 'สำเนาทะเบียนบ้าน', req: true },
      { seq: 15, key: 'id_card_spouse_g2',   label: 'สำเนาบัตรประชาชน/ข้าราชการของคู่สมรส' },
      { seq: 16, key: 'house_reg_spouse_g2', label: 'สำเนาทะเบียนบ้านของคู่สมรส' },
      { seq: 17, key: 'marriage_cert_g2',    label: 'สำเนาทะเบียนสมรส' },
    ],
  },
  {
    group: 'อื่นๆ',
    items: [
      { seq: 18, key: 'name_change', label: 'สำเนาการเปลี่ยนชื่อ – สกุล / ใบหย่า (ผู้เกี่ยวข้องกับสัญญากู้)' },
      { seq: 0,  key: 'other',       label: 'เอกสารอื่นๆ' },
    ],
  },
]

// Spouse doc keys — required เฉพาะเมื่อสมรส
const BORROWER_SPOUSE_KEYS = ['id_card_spouse', 'house_reg_spouse', 'marriage_cert']

// Guarantor spouse keys แยกตาม index
const G1_SPOUSE_KEYS = ['id_card_spouse_g1', 'house_reg_spouse_g1', 'marriage_cert_g1']
const G2_SPOUSE_KEYS = ['id_card_spouse_g2', 'house_reg_spouse_g2', 'marriage_cert_g2']

// effective required: ผสมระหว่าง req ใน definition + marital status
function isEffectivelyRequired(item: DocItem): boolean {
  if (item.system) return false
  if (item.req) return true
  // spouse docs — required เฉพาะเมื่อคนนั้นสมรส
  if (BORROWER_SPOUSE_KEYS.includes(item.key)) return form.step1.marital_status === 'married'
  if (G1_SPOUSE_KEYS.includes(item.key)) return form.step3.guarantors[0]?.marital_status === 'married'
  if (G2_SPOUSE_KEYS.includes(item.key)) return form.step3.guarantors[1]?.marital_status === 'married'
  return false
}

// uploadable items only (ไม่รวม system-generated)
const uploadableItems = docRequirements
  .flatMap(g => g.items)
  .filter(i => !i.system)

const isUploaded = (key: string) => attachments.value.some(a => a.file_type === key)

async function loadAttachments() {
  if (!form.draftId) return
  try {
    attachments.value = await attachmentService.list(form.draftId)
  } catch {
    toast.show('โหลดรายการเอกสารไม่สำเร็จ', 'error')
  }
}

onMounted(loadAttachments)

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (!target.files?.length || !form.draftId) return

  uploading.value = true
  const file = target.files[0]
  try {
    await attachmentService.upload(form.draftId, file, selectedType.value)
    target.value = ''
    await loadAttachments()
    toast.show(`อัปโหลด "${file.name}" สำเร็จ`, 'success')
  } catch (err: any) {
    toast.show(err.response?.data?.detail || 'อัปโหลดล้มเหลว', 'error')
  } finally {
    uploading.value = false
  }
}

function askDelete(id: string) { confirmDeleteId.value = id }

async function confirmDelete() {
  if (!confirmDeleteId.value) return
  deleting.value = true
  try {
    await attachmentService.remove(confirmDeleteId.value)
    await loadAttachments()
    toast.show('ลบไฟล์เรียบร้อยแล้ว', 'success')
  } catch {
    toast.show('ลบไฟล์ไม่สำเร็จ', 'error')
  } finally {
    deleting.value = false
    confirmDeleteId.value = null
  }
}

function formatSize(bytes: number) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function labelOf(key: string) {
  return uploadableItems.find(i => i.key === key)?.label ?? key
}
</script>

<template>
  <div class="space-y-6">
    <header class="flex justify-between items-end">
      <div>
        <h2 class="text-2xl font-black text-primary">เอกสารประกอบการขอกู้เงิน</h2>
        <p class="text-base-content/60 italic text-sm">อ้างอิงตามระเบียบสหกรณ์ฯ (18 รายการ)</p>
      </div>
      <button @click="showGuide = true" class="btn btn-sm btn-outline btn-primary gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        ดูใบรายการต้นฉบับ
      </button>
    </header>

    <div v-if="!form.draftId" class="alert alert-warning shadow-lg border-none rounded-2xl p-6">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <div>
        <h3 class="font-bold">ยังไม่สามารถอัปโหลดได้</h3>
        <div class="text-xs">กรุณากด "บันทึกร่าง" ในขั้นตอนที่ 1 หรือ 2 ก่อน เพื่อให้ระบบสร้างเลขที่อ้างอิง</div>
      </div>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-8">

      <!-- Left: Checklist 18 รายการ -->
      <aside class="lg:col-span-5 space-y-4">
        <div class="card bg-base-200/50 border border-base-300">
          <div class="card-body p-4">
            <h3 class="font-black text-xs uppercase tracking-widest text-base-content/50 mb-3">รายการตรวจสอบเอกสาร (18 รายการ)</h3>

            <div v-for="group in docRequirements" :key="group.group" class="mb-4 last:mb-0">
              <p class="text-[10px] font-bold text-primary uppercase tracking-wider mb-2">{{ group.group }}</p>
              <div class="space-y-1">
                <div
                  v-for="item in group.items"
                  :key="item.key"
                  class="flex items-start gap-2 p-2 rounded-lg text-xs transition-all"
                  :class="[
                    item.system
                      ? 'bg-base-300/60 opacity-70'
                      : isUploaded(item.key)
                        ? 'bg-success/10'
                        : 'bg-white/60'
                  ]"
                >
                  <!-- seq badge -->
                  <span class="shrink-0 w-5 h-5 rounded-full text-[10px] font-black flex items-center justify-center mt-0.5"
                    :class="item.system
                      ? 'bg-base-content/20 text-base-content/50'
                      : isUploaded(item.key)
                        ? 'bg-success text-white'
                        : isEffectivelyRequired(item)
                          ? 'bg-error/20 text-error'
                          : 'bg-base-300 text-base-content/40'
                    ">
                    <template v-if="!item.system && isUploaded(item.key)">✓</template>
                    <template v-else-if="item.system">–</template>
                    <template v-else-if="item.seq > 0">{{ item.seq }}</template>
                    <template v-else>+</template>
                  </span>

                  <!-- label -->
                  <div class="flex-1 min-w-0">
                    <span :class="[
                      isEffectivelyRequired(item) ? 'font-bold' : '',
                      isUploaded(item.key) ? 'line-through text-base-content/40' : ''
                    ]">{{ item.label }}</span>
                    <span v-if="item.note" class="ml-1 text-base-content/40">({{ item.note }})</span>
                    <span v-if="item.system" class="ml-1 text-base-content/40 italic">ระบบสร้างให้</span>
                    <span v-else-if="isEffectivelyRequired(item)" class="ml-1 text-error text-[10px]">*จำเป็น</span>
                    <span v-else-if="[...BORROWER_SPOUSE_KEYS, ...G1_SPOUSE_KEYS, ...G2_SPOUSE_KEYS].includes(item.key)"
                          class="ml-1 text-warning text-[10px]">จำเป็นหากสมรส</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- Right: Upload & List -->
      <main class="lg:col-span-7 space-y-6">

        <!-- Upload Box -->
        <div class="card bg-primary text-primary-content shadow-xl overflow-hidden">
          <div class="card-body p-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
              <div class="form-control">
                <label class="label"><span class="label-text text-white/70 font-bold text-xs uppercase">1. เลือกประเภทเอกสาร</span></label>
                <select v-model="selectedType" class="select select-bordered w-full text-base-content bg-white border-none rounded-xl">
                  <optgroup v-for="group in docRequirements" :key="group.group" :label="group.group">
                    <option
                      v-for="item in group.items.filter(i => !i.system)"
                      :key="item.key"
                      :value="item.key"
                    >
                      {{ item.seq > 0 ? `${item.seq}. ` : '' }}{{ item.label }}
                    </option>
                  </optgroup>
                </select>
              </div>

              <div class="form-control">
                <label class="label"><span class="label-text text-white/70 font-bold text-xs uppercase">2. เลือกไฟล์ (ไม่เกิน 10MB)</span></label>
                <input
                  type="file"
                  class="file-input file-input-bordered bg-white w-full text-base-content border-none rounded-xl"
                  :accept="system.config?.storage?.allowed_mimes?.includes('application/pdf') ? '.pdf,.jpg,.jpeg,.png' : '*'"
                  :disabled="uploading"
                  @change="handleFileUpload"
                />
              </div>
            </div>

            <div v-if="uploading" class="mt-4 flex items-center gap-2 text-xs font-bold">
              <span class="loading loading-spinner loading-xs"></span> กำลังอัปโหลด...
            </div>
          </div>
        </div>

        <!-- Files List -->
        <div class="space-y-3">
          <h3 class="text-sm font-bold flex items-center gap-2">
            <span class="w-1.5 h-4 bg-primary rounded-full"></span>
            รายการไฟล์ที่อัปโหลดแล้ว ({{ attachments.length }})
          </h3>

          <div v-if="attachments.length === 0" class="py-12 border-2 border-dashed border-base-300 rounded-3xl text-center text-base-content/30 italic text-sm">
            ยังไม่มีไฟล์ถูกส่งขึ้นระบบ
          </div>

          <div v-else class="grid grid-cols-1 gap-3">
            <div
              v-for="file in attachments"
              :key="file.id"
              class="flex items-center justify-between p-4 bg-white border border-base-200 rounded-2xl shadow-sm hover:shadow-md transition-all"
            >
              <div class="flex items-center gap-4 min-w-0">
                <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary text-xs font-black shrink-0">
                  PDF
                </div>
                <div class="min-w-0">
                  <p class="font-bold text-sm truncate">{{ file.original_filename }}</p>
                  <p class="text-[10px] text-base-content/40 font-bold uppercase tracking-wider">
                    {{ labelOf(file.file_type) }} · {{ formatSize(file.file_size_bytes) }}
                  </p>
                </div>
              </div>
              <button @click="askDelete(file.id)" class="btn btn-ghost btn-circle btn-sm text-error shrink-0">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Delete Confirm Modal -->
    <dialog class="modal" :class="{ 'modal-open': confirmDeleteId }">
      <div class="modal-box max-w-sm rounded-2xl shadow-2xl">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-error/10 flex items-center justify-center shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </div>
          <div>
            <h3 class="font-black text-base">ยืนยันการลบไฟล์</h3>
            <p class="text-sm text-base-content/60">ไฟล์จะถูกลบออกจากระบบถาวร ไม่สามารถกู้คืนได้</p>
          </div>
        </div>
        <div class="modal-action mt-2">
          <button class="btn btn-ghost btn-sm" :disabled="deleting" @click="confirmDeleteId = null">ยกเลิก</button>
          <button class="btn btn-error btn-sm text-white" :disabled="deleting" @click="confirmDelete">
            <span v-if="deleting" class="loading loading-spinner loading-xs"></span>
            ลบไฟล์
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="confirmDeleteId = null"><button>close</button></form>
    </dialog>

    <!-- Original Guide Lightbox -->
    <dialog class="modal" :class="{ 'modal-open': showGuide }">
      <div class="modal-box max-w-4xl p-0 overflow-hidden bg-white rounded-3xl shadow-2xl">
        <div class="bg-base-200 p-4 flex justify-between items-center sticky top-0 z-10">
          <h3 class="font-black text-sm uppercase tracking-widest">รายการเอกสารประกอบ (ระเบียบสหกรณ์ฯ)</h3>
          <button @click="showGuide = false" class="btn btn-sm btn-circle btn-ghost">✕</button>
        </div>
        <div class="p-4 max-h-[80vh] overflow-auto">
          <img src="@/assets/guides/document_guide.png" class="w-full h-auto" alt="Document Guide" />
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="showGuide = false"><button>close</button></form>
    </dialog>
  </div>
</template>
