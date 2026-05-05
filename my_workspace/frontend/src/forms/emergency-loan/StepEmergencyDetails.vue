<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import type { StepEmergencyData } from '@/types/form'

const props = defineProps<{
  modelValue: StepEmergencyData
}>()

const emit = defineEmits(['update:modelValue'])

const localData = ref<StepEmergencyData>({ ...props.modelValue })

watch(localData, (val) => {
  emit('update:modelValue', val)
}, { deep: true })

onMounted(() => {
  if (!localData.value.payout_method) localData.value.payout_method = 'transfer'
})
</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <header class="text-center">
      <h2 class="text-2xl font-black text-primary">รายละเอียดการกู้ฉุกเฉิน</h2>
      <p class="text-base-content/60 text-sm">วงเงินกู้สูงสุดไม่เกิน 50,000 บาท</p>
    </header>

    <div class="card bg-base-100 shadow-xl border border-base-200 overflow-hidden">
      <div class="card-body p-8 space-y-6">
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <!-- Loan Amount -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-bold">จำนวนเงินที่ขอกู้ (บาท)</span>
              <span class="label-text-alt text-error font-bold">สูงสุด 50,000</span>
            </label>
            <div class="relative group">
              <input 
                v-model.number="localData.loan_amount"
                type="number" 
                placeholder="0.00"
                max="50000"
                class="input input-bordered w-full pl-12 text-lg font-black focus:border-primary transition-all group-hover:border-primary/50"
              />
              <div class="absolute left-4 top-1/2 -translate-y-1/2 text-base-content/30 font-black group-focus-within:text-primary transition-colors">฿</div>
            </div>
          </div>

          <!-- Repayment Period -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-bold">จำนวนงวดที่ต้องการส่งคืน</span>
              <span class="label-text-alt text-base-content/50">สูงสุด 12 งวด</span>
            </label>
            <select v-model.number="localData.repayment_period" class="select select-bordered w-full font-bold">
              <option :value="null" disabled>เลือกจำนวนงวด</option>
              <option v-for="n in 12" :key="n" :value="n">{{ n }} งวด</option>
            </select>
          </div>
        </div>

        <!-- Loan Purpose -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-bold">เหตุผลความจำเป็นในการขอกู้</span>
          </label>
          <textarea 
            v-model="localData.loan_purpose"
            placeholder="โปรดระบุรายละเอียดความจำเป็น..."
            class="textarea textarea-bordered h-32 font-medium leading-relaxed focus:border-primary"
          ></textarea>
        </div>

        <!-- Payout Method -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-bold text-xs uppercase tracking-widest text-base-content/40">วิธีการรับเงิน</span>
          </label>
          <div class="flex gap-4">
            <label class="flex-1 cursor-pointer">
              <input type="radio" v-model="localData.payout_method" value="transfer" class="hidden peer" />
              <div class="p-4 border-2 rounded-2xl text-center font-bold transition-all peer-checked:border-primary peer-checked:bg-primary/5 peer-checked:text-primary hover:border-primary/30">
                โอนเข้าบัญชี
              </div>
            </label>
            <label class="flex-1 cursor-pointer">
              <input type="radio" v-model="localData.payout_method" value="cash" class="hidden peer" />
              <div class="p-4 border-2 rounded-2xl text-center font-bold transition-all peer-checked:border-primary peer-checked:bg-primary/5 peer-checked:text-primary hover:border-primary/30">
                รับเงินสด
              </div>
            </label>
          </div>
        </div>

      </div>
    </div>
    
    <div class="alert alert-info shadow-sm border-none bg-info/10 text-info font-bold text-xs">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
      <span>หมายเหตุ: การกู้ฉุกเฉินใช้เพื่อบรรเทาความเดือดร้อนที่เกิดขึ้นกะทันหันเท่านั้น</span>
    </div>
  </div>
</template>
