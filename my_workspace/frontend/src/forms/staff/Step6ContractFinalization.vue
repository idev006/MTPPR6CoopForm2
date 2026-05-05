<script setup lang="ts">
import { ref } from 'vue'
import { useFormStore } from '@/stores/form.store'
import UiInput from '@/components/ui/UiInput.vue'
import UiSignaturePad from '@/components/ui/UiSignaturePad.vue'
import type { SignatureData } from '@/types/form'

const form = useFormStore()
const signingActor = ref<{ id: 'manager' | 'chairman'; label: string } | null>(null)

function startSigning(actor: 'manager' | 'chairman', label: string) {
  signingActor.value = { id: actor, label }
}

function handleSaveSignature(base64: string) {
  if (!signingActor.value) return
  const sig: SignatureData = {
    signed: true,
    signed_at: new Date().toISOString(),
    signature_base64: base64
  }
  if (signingActor.value.id === 'manager') form.step6.manager_sig = sig
  else if (signingActor.value.id === 'chairman') form.step6.chairman_sig = sig
  else if (signingActor.value.id === 'witness1') form.step6.witness_sig_1 = sig
  else if (signingActor.value.id === 'witness2') form.step6.witness_sig_2 = sig
  
  form.markDirty()
  signingActor.value = null
}

function updateField(field: keyof typeof form.step6, value: any) {
  (form.step6 as any)[field] = value
  form.markDirty()
}
</script>

<template>
  <div class="space-y-8">
    <header class="text-center border-b border-base-200 pb-6">
      <h2 class="text-2xl font-bold text-secondary">การออกสัญญาและอนุมัติ</h2>
      <p class="text-base-content/60 italic text-sm">ขั้นตอนสุดท้ายสำหรับการอนุมัติเงินกู้</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Contract Info -->
      <div class="space-y-4">
        <h3 class="font-bold text-lg flex items-center gap-2 text-secondary">
          <span class="w-2 h-2 bg-secondary rounded-full"></span>
          รายละเอียดเลขที่สัญญา
        </h3>
        <div class="grid grid-cols-1 gap-4 bg-base-200/50 p-6 rounded-2xl border border-base-300">
          <UiInput 
            label="เลขที่สัญญา" placeholder="เช่น 123/2567"
            :model-value="form.step6.contract_no" @update:model-value="updateField('contract_no', $event)" 
          />
          <div class="grid grid-cols-2 gap-4">
            <UiInput 
              label="อัตราดอกเบี้ย (%)" type="number"
              :model-value="form.step6.interest_rate" @update:model-value="updateField('interest_rate', $event)" 
            />
            <UiInput 
              label="วันที่เริ่มสัญญา" type="date"
              :model-value="form.step6.effective_date" @update:model-value="updateField('effective_date', $event)" 
            />
          </div>
        </div>

        <!-- Witnesses -->
        <h3 class="font-bold text-lg flex items-center gap-2 text-secondary pt-4">
          <span class="w-2 h-2 bg-secondary rounded-full"></span>
          พยาน (Witnesses)
        </h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <!-- Witness 1 -->
          <div class="flex flex-col p-4 bg-white border border-base-300 rounded-xl shadow-sm gap-2">
            <p class="text-[10px] uppercase font-bold text-base-content/40">พยานคนที่ 1</p>
            <UiInput label="ชื่อ-นามสกุลพยาน 1" size="sm" placeholder="เช่น พ.ต.ต. วีระ สุขใจ"
              :model-value="form.step6.witness_1_name" @update:model-value="updateField('witness_1_name', $event)" />
            <div class="h-16 flex items-center justify-center bg-base-100 rounded border border-dashed border-base-300 overflow-hidden group relative">
              <img v-if="form.step6.witness_sig_1.signed" :src="form.step6.witness_sig_1.signature_base64" class="h-full object-contain" />
              <span v-else class="text-xs text-base-content/30 italic">ยังไม่ได้ลงนาม</span>
              <button
                class="absolute inset-0 bg-secondary/80 text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-xs font-bold"
                @click="startSigning('witness1', 'พยานคนที่ 1')"
              >เซ็นชื่อ</button>
            </div>
          </div>
          <!-- Witness 2 -->
          <div class="flex flex-col p-4 bg-white border border-base-300 rounded-xl shadow-sm gap-2">
            <p class="text-[10px] uppercase font-bold text-base-content/40">พยานคนที่ 2</p>
            <UiInput label="ชื่อ-นามสกุลพยาน 2" size="sm" placeholder="เช่น ด.ต. มานะ ตั้งใจ"
              :model-value="form.step6.witness_2_name" @update:model-value="updateField('witness_2_name', $event)" />
            <div class="h-16 flex items-center justify-center bg-base-100 rounded border border-dashed border-base-300 overflow-hidden group relative">
              <img v-if="form.step6.witness_sig_2.signed" :src="form.step6.witness_sig_2.signature_base64" class="h-full object-contain" />
              <span v-else class="text-xs text-base-content/30 italic">ยังไม่ได้ลงนาม</span>
              <button
                class="absolute inset-0 bg-secondary/80 text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-xs font-bold"
                @click="startSigning('witness2', 'พยานคนที่ 2')"
              >เซ็นชื่อ</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Approval Signatures -->
      <div class="space-y-4">
        <h3 class="font-bold text-lg flex items-center gap-2 text-secondary">
          <span class="w-2 h-2 bg-secondary rounded-full"></span>
          ผู้มีอำนาจอนุมัติ
        </h3>
        <div class="grid grid-cols-1 gap-4">
          <!-- Manager -->
          <div class="p-4 bg-white border border-base-300 rounded-xl shadow-sm space-y-2">
            <p class="text-[10px] uppercase font-bold text-base-content/40">ผู้จัดการ</p>
            <UiInput label="ชื่อ-นามสกุลผู้จัดการ" size="sm" placeholder="เช่น นางสาวสมฤดี บริหารดี"
              :model-value="form.step6.manager_name" @update:model-value="updateField('manager_name', $event)" />
            <div class="flex items-center justify-between">
              <div v-if="form.step6.manager_sig.signed" class="h-14 flex items-center flex-1">
                <img :src="form.step6.manager_sig.signature_base64" class="h-full object-contain" />
              </div>
              <p v-else class="text-sm italic text-base-content/30 py-3 flex-1">ยังไม่ได้ลงนาม</p>
              <button class="btn btn-sm btn-outline btn-secondary" @click="startSigning('manager', 'ผู้จัดการ')">
                {{ form.step6.manager_sig.signed ? 'เซ็นใหม่' : 'ลงนาม' }}
              </button>
            </div>
          </div>

          <!-- Chairman -->
          <div class="p-4 bg-white border border-base-300 rounded-xl shadow-sm space-y-2">
            <p class="text-[10px] uppercase font-bold text-base-content/40">ประธานกรรมการ</p>
            <UiInput label="ชื่อ-นามสกุลประธาน" size="sm" placeholder="เช่น นายอุดม สหกรณ์ดี"
              :model-value="form.step6.chairman_name" @update:model-value="updateField('chairman_name', $event)" />
            <div class="flex items-center justify-between">
              <div v-if="form.step6.chairman_sig.signed" class="h-14 flex items-center flex-1">
                <img :src="form.step6.chairman_sig.signature_base64" class="h-full object-contain" />
              </div>
              <p v-else class="text-sm italic text-base-content/30 py-3 flex-1">ยังไม่ได้ลงนาม</p>
              <button class="btn btn-sm btn-outline btn-secondary" @click="startSigning('chairman', 'ประธานกรรมการ')">
                {{ form.step6.chairman_sig.signed ? 'เซ็นใหม่' : 'ลงนาม' }}
              </button>
            </div>
          </div>
        </div>

        <div class="alert alert-info mt-8 py-3 text-xs leading-relaxed">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <span>ตรวจสอบข้อมูลให้ถูกต้องก่อนกดอนุมัติ การออกเลขสัญญาจะมีผลต่อระบบบัญชีสหกรณ์</span>
        </div>
      </div>
    </div>

    <!-- Final Action -->
    <div class="flex flex-col items-center justify-center p-8 border-t border-base-200 gap-4">
      <div class="alert alert-warning max-w-md text-xs py-2">
        <span>เมื่อกด "อนุมัติและปิดเล่มสัญญา" ระบบจะทำการออกเลขสัญญาและบันทึกข้อมูลถาวร</span>
      </div>
      <button class="btn btn-success btn-lg px-12 text-white shadow-lg" :disabled="!form.step6.contract_no">
        อนุมัติและปิดเล่มสัญญา
      </button>
    </div>

    <!-- Signature Pad Modal -->
    <UiSignaturePad 
      v-if="signingActor"
      :title="`ลงนามโดย ${signingActor.label}`"
      @save="handleSaveSignature"
      @cancel="signingActor = null"
    />
  </div>
</template>
