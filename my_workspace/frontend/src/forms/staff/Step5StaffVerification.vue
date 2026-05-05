<script setup lang="ts">
import { useFormStore } from '@/stores/form.store'
import UiInput from '@/components/ui/UiInput.vue'

const form = useFormStore()

const CHECKLIST_LABELS = [
  'สำเนาบัตรประจำตัวประชาชน/บัตรข้าราชการ (ผู้กู้)',
  'สำเนาทะเบียนบ้าน (ผู้กู้)',
  'สลิปเงินเดือนเดือนล่าสุด (ผู้กู้)',
  'สำเนาบัตรประจำตัวประชาชน (คู่สมรส)',
  'สำเนาทะเบียนบ้าน (คู่สมรส)',
  'ใบสำคัญการสมรส / ใบสำคัญการหย่า',
  'สำเนาบัตรประจำตัวประชาชน (ผู้ค้ำประกันทุกคน)',
  'สำเนาทะเบียนบ้าน (ผู้ค้ำประกันทุกคน)',
  'ใบเปลี่ยนชื่อ-นามสกุล (ถ้ามี)',
  'หนังสือยินยอมให้หักเงินเดือน (ผู้กู้)',
  'หนังสือยินยอมให้หักเงินเดือน (ผู้ค้ำประกัน)',
  'สัญญาเดิม (กรณีกู้ใหม่เพื่อหักลบหนี้เดิม)',
  'เอกสารแสดงวัตถุประสงค์การกู้ (เช่น ใบจอง, ใบเสนอราคา)',
  'ใบแสดงยอดหนี้คงเหลือจากสถาบันการเงินอื่น (ถ้ามี)',
  'ภาพถ่ายหน้าบัญชีธนาคาร (กรณีโอนผ่านธนาคาร)',
  'การตรวจสอบฐานข้อมูลเครดิต (ถ้ามี)',
  'ตรวจสอบความถูกต้องของลายมือชื่อทุกแห่ง',
  'ตรวจสอบสถานะสมาชิกภาพและหุ้นสะสม'
]

function toggleCheck(idx: number) {
  form.step5.checklist_items[idx] = !form.step5.checklist_items[idx]
  form.markDirty()
}

function updateLimit(field: keyof typeof form.step5.limit_analysis, value: number) {
  form.step5.limit_analysis[field] = value
  form.step5.limit_analysis.net_income = form.step5.limit_analysis.total_income - form.step5.limit_analysis.total_deduction
  form.markDirty()
}
</script>

<template>
  <div class="space-y-8">
    <header class="text-center border-b border-base-200 pb-6">
      <h2 class="text-2xl font-bold text-primary">การตรวจสอบและพิจารณาสิทธิ์</h2>
      <p class="text-base-content/60 italic text-sm">สำหรับเจ้าหน้าที่สหกรณ์เท่านั้น</p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Left: Checklist -->
      <div class="lg:col-span-2 space-y-4">
        <h3 class="font-bold flex items-center gap-2">
          <span class="badge badge-neutral badge-sm">1</span> 
          ตรวจสอบความครบถ้วนของเอกสาร (Checklist)
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2 bg-base-200/30 p-4 rounded-2xl border border-base-300">
          <label 
            v-for="(label, idx) in CHECKLIST_LABELS" 
            :key="idx"
            class="flex items-start gap-3 p-2 rounded-lg hover:bg-base-200 cursor-pointer transition-colors"
          >
            <input 
              type="checkbox" 
              :checked="form.step5.checklist_items[idx]" 
              @change="toggleCheck(idx)"
              class="checkbox checkbox-primary checkbox-sm mt-0.5" 
            />
            <span class="text-xs leading-relaxed">{{ idx + 1 }}. {{ label }}</span>
          </label>
        </div>
      </div>

      <!-- Right: Financial Analysis -->
      <div class="space-y-6">
        <div class="card bg-base-200 border border-base-300 shadow-sm">
          <div class="card-body p-4 space-y-4">
            <h3 class="font-bold flex items-center gap-2">
              <span class="badge badge-neutral badge-sm">2</span> 
              วิเคราะห์วงเงินและรายได้
            </h3>
            
            <UiInput 
              label="รวมรายได้ต่อเดือน" type="number" size="sm"
              :model-value="form.step5.limit_analysis.total_income" 
              @update:model-value="updateLimit('total_income', $event)" 
            />
            <UiInput 
              label="รวมรายจ่าย/หนี้สินที่หัก" type="number" size="sm"
              :model-value="form.step5.limit_analysis.total_deduction" 
              @update:model-value="updateLimit('total_deduction', $event)" 
            />

            <div class="divider my-0"></div>

            <div class="flex justify-between items-center">
              <span class="text-sm font-medium">คงเหลือสุทธิ (Net)</span>
              <span class="text-lg font-bold" :class="form.step5.limit_analysis.net_income < 0 ? 'text-error' : 'text-success'">
                {{ form.step5.limit_analysis.net_income.toLocaleString() }}
              </span>
            </div>

            <div class="alert alert-info py-2 text-[10px] leading-tight">
              <span>* ต้องมีเงินคงเหลือสุทธิไม่น้อยกว่าร้อยละ 30 ของเงินได้รายเดือน</span>
            </div>
          </div>
        </div>

        <div class="card bg-primary/5 border border-primary/20 shadow-sm">
          <div class="card-body p-4">
            <h3 class="font-bold text-sm mb-2">ความเห็นผู้บังคับบัญชา (จากระบบ)</h3>
            <div v-if="form.step4.superior_sig.signed" class="space-y-2">
              <div class="flex items-center gap-2">
                <span :class="form.step4.superior_opinion === 'true' ? 'badge badge-success' : 'badge badge-error'" class="badge-sm">
                  {{ form.step4.superior_opinion === 'true' ? 'เห็นควรสนับสนุน' : 'ไม่เห็นควรสนับสนุน' }}
                </span>
              </div>
              <div class="bg-white p-2 rounded border border-base-300 h-16 flex items-center justify-center overflow-hidden">
                <img :src="form.step4.superior_sig.signature_base64" class="h-full object-contain" />
              </div>
              <p class="text-[10px] text-base-content/40 text-center">ลงนามเมื่อ {{ new Date(form.step4.superior_sig.signed_at!).toLocaleDateString('th-TH') }}</p>
            </div>
            <div v-else class="text-center py-4 text-base-content/30 italic text-xs">ยังไม่มีข้อมูลการลงนาม</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
