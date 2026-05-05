<script setup lang="ts">
import type { Step2Data } from '@/types/form'
import UiInput from '@/components/ui/UiInput.vue'

const props = defineProps<{ modelValue: Step2Data }>()
const emit = defineEmits<{ 'update:modelValue': [Step2Data] }>()

function update<K extends keyof Step2Data>(field: K, value: Step2Data[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
}

const LOAN_PURPOSES = [
  'ชำระหนี้สิน', 'ซื้อที่ดิน / ที่อยู่อาศัย',
  'ปรับปรุง / ต่อเติมที่พักอาศัย', 'ซื้อยานพาหนะ',
  'การศึกษา', 'การรักษาพยาบาล', 'การเกษตร', 'อื่นๆ',
]
</script>

<template>
  <div class="space-y-6">
    <section>
      <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
        <span class="w-1 h-6 bg-primary rounded-full"></span>
        รายละเอียดเงินกู้
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <UiInput 
          label="จำนวนเงินกู้ (บาท)" type="number" :required="true"
          :model-value="modelValue.loan_amount" @update:model-value="update('loan_amount', $event)" 
        />
        <UiInput 
          label="จำนวนงวดที่ขอผ่อน (งวด)" type="number" :required="true"
          :model-value="modelValue.repayment_period" @update:model-value="update('repayment_period', $event)" 
        />
        <div class="sm:col-span-2">
          <label class="label text-sm font-bold">วัตถุประสงค์ในการขอกู้ <span class="text-error">*</span></label>
          <select
            :value="modelValue.loan_purpose"
            @change="update('loan_purpose', ($event.target as HTMLSelectElement).value)"
            class="select select-bordered w-full"
          >
            <option value="" disabled>-- เลือกวัตถุประสงค์ --</option>
            <option v-for="p in LOAN_PURPOSES" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>
      </div>

      <!-- Quick Summary -->
      <div v-if="modelValue.loan_amount && modelValue.repayment_period" class="mt-4 p-4 bg-primary/5 border border-primary/10 rounded-xl">
        <div class="flex justify-between items-center">
          <span class="text-sm text-base-content/60">ประมาณการเงินต้นต่องวด</span>
          <span class="text-xl font-bold text-primary">
            {{ Math.ceil(modelValue.loan_amount / modelValue.repayment_period).toLocaleString('th-TH') }}
            <span class="text-sm font-normal">บาท</span>
          </span>
        </div>
      </div>
    </section>

    <section>
      <h3 class="text-lg font-bold mb-4 flex items-center gap-2 text-secondary">
        <span class="w-1 h-6 bg-secondary rounded-full"></span>
        วิธีการรับเงินกู้
      </h3>
      
      <div class="flex flex-col sm:flex-row gap-4 mb-4">
        <label class="flex items-center gap-3 p-4 border rounded-xl cursor-pointer hover:bg-base-200 transition-colors flex-1"
          :class="{ 'border-secondary bg-secondary/5': modelValue.payout_method === 'transfer' }">
          <input type="radio" name="payout" class="radio radio-secondary" 
            :checked="modelValue.payout_method === 'transfer'" @change="update('payout_method', 'transfer')" />
          <div>
            <p class="font-bold">โอนเข้าบัญชีธนาคาร</p>
            <p class="text-xs text-base-content/50">รับเงินสะดวกรวดเร็ว</p>
          </div>
        </label>
        
        <label class="flex items-center gap-3 p-4 border rounded-xl cursor-pointer hover:bg-base-200 transition-colors flex-1"
          :class="{ 'border-secondary bg-secondary/5': modelValue.payout_method === 'cheque' }">
          <input type="radio" name="payout" class="radio radio-secondary" 
            :checked="modelValue.payout_method === 'cheque'" @change="update('payout_method', 'cheque')" />
          <div>
            <p class="font-bold">รับเป็นเช็ค</p>
            <p class="text-xs text-base-content/50">รับที่สำนักงานสหกรณ์</p>
          </div>
        </label>
      </div>

      <!-- Bank Details (Show if transfer) -->
      <div v-if="modelValue.payout_method === 'transfer'" class="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 bg-base-200/50 rounded-xl border border-base-300">
        <UiInput 
          label="ชื่อธนาคาร" placeholder="เช่น กรุงไทย, ทหารไทยธนชาต"
          :model-value="modelValue.bank_name" @update:model-value="update('bank_name', $event)" 
        />
        <UiInput 
          label="เลขที่บัญชี" 
          :model-value="modelValue.bank_account_no" @update:model-value="update('bank_account_no', $event)" 
        />
        <div class="sm:col-span-2">
          <UiInput 
            label="ชื่อบัญชี (ต้องเป็นชื่อผู้ขอกู้เท่านั้น)" 
            :model-value="modelValue.bank_account_name" @update:model-value="update('bank_account_name', $event)" 
          />
        </div>
      </div>
    </section>
  </div>
</template>
