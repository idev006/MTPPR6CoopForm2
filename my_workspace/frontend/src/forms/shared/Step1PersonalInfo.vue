<script setup lang="ts">
import type { Step1Data, AddressInfo } from '@/types/form'
import UiInput from '@/components/ui/UiInput.vue'
import AddressFields from '@/components/AddressFields.vue'

const props = defineProps<{ modelValue: Step1Data }>()
const emit = defineEmits<{ 'update:modelValue': [Step1Data] }>()

function updateField(field: keyof Step1Data, value: any) {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
}

function updateAddr(type: 'current_addr' | 'register_addr', value: AddressInfo) {
  emit('update:modelValue', { ...props.modelValue, [type]: value })
}
</script>

<template>
  <div class="space-y-6">
    <section>
      <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
        <span class="w-1 h-6 bg-primary rounded-full"></span>
        ข้อมูลส่วนตัวผู้กู้
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <UiInput label="ยศ / คำนำหน้า" :required="true" placeholder="เช่น นาย, นาง, ร.ต."
          :model-value="modelValue.title" @update:model-value="updateField('title', $event)" />
        <UiInput label="ชื่อ" :required="true"
          :model-value="modelValue.first_name" @update:model-value="updateField('first_name', $event)" />
        <UiInput label="นามสกุล" :required="true"
          :model-value="modelValue.last_name" @update:model-value="updateField('last_name', $event)" />
        <UiInput label="ตำแหน่ง" :required="true"
          :model-value="modelValue.position" @update:model-value="updateField('position', $event)" />
        <UiInput label="รหัสสมาชิก" :required="true"
          :model-value="modelValue.member_code" @update:model-value="updateField('member_code', $event)" />
        <UiInput label="โทรศัพท์" type="tel" :required="true"
          :model-value="modelValue.phone" @update:model-value="updateField('phone', $event)" />
        <UiInput label="เลขบัตรประชาชน" :required="true" maxlength="13"
          :model-value="modelValue.id_card" @update:model-value="updateField('id_card', $event)" />
        <UiInput label="สังกัด / กรม" :required="true"
          :model-value="modelValue.department" @update:model-value="updateField('department', $event)" />
        <UiInput label="หน่วยงาน"
          :model-value="modelValue.organization" @update:model-value="updateField('organization', $event)" />
      </div>

      <div class="divider text-xs font-bold uppercase tracking-wider text-base-content/40 my-4">สถานะภาพ</div>
      
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div class="sm:col-span-1 flex items-center gap-6">
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="radio" name="marital" class="radio radio-primary" 
              :checked="modelValue.marital_status === 'single'" @change="updateField('marital_status', 'single')" />
            <span class="font-bold">โสด</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="radio" name="marital" class="radio radio-primary" 
              :checked="modelValue.marital_status === 'married'" @change="updateField('marital_status', 'married')" />
            <span class="font-bold">สมรส</span>
          </label>
        </div>
        
        <div v-if="modelValue.marital_status === 'married'" class="sm:col-span-3">
          <UiInput label="ชื่อ-นามสกุล คู่สมรส (ที่ถูกต้องตามกฎหมาย)" :required="true"
            :model-value="modelValue.spouse_name" @update:model-value="updateField('spouse_name', $event)" />
        </div>
      </div>
    </section>

    <section class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <AddressFields title="ที่อยู่ปัจจุบัน" :model-value="modelValue.current_addr" @update:model-value="updateAddr('current_addr', $event)" />
      <AddressFields title="ที่อยู่ตามทะเบียนบ้าน" :model-value="modelValue.register_addr" @update:model-value="updateAddr('register_addr', $event)" />
    </section>

    <section>
      <h3 class="text-lg font-bold mb-4 flex items-center gap-2 text-success">
        <span class="w-1 h-6 bg-success rounded-full"></span>
        ข้อมูลรายได้และฐานะทางการเงิน
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <UiInput label="เงินเดือน (บาท)" type="number"
          :model-value="modelValue.salary" @update:model-value="updateField('salary', $event)" />
        <UiInput label="ทุนเรือนหุ้นสะสม (บาท)" type="number"
          :model-value="modelValue.shares_amount" @update:model-value="updateField('shares_amount', $event)" />
        <UiInput label="หนี้เดิมคงเหลือ (บาท)" type="number"
          :model-value="modelValue.existing_debt" @update:model-value="updateField('existing_debt', $event)" />
      </div>
    </section>
  </div>
</template>
