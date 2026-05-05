<script setup lang="ts">
import { computed } from 'vue'
import type { MemberProfileUpdate } from '@/types/member'
import UiInput from './ui/UiInput.vue'
import AddressFields, { type AddressData } from './AddressFields.vue'

const props = defineProps<{
  modelValue: MemberProfileUpdate
  saving: boolean
  saved: boolean
  errorMsg: string
}>()

const emit = defineEmits<{
  'update:modelValue': [MemberProfileUpdate]
  save: []
}>()

function updateField(field: keyof MemberProfileUpdate, value: string) {
  emit('update:modelValue', { ...props.modelValue, [field]: value || null })
}

const addressModel = computed<AddressData>({
  get: () => ({
    addr_house_no: props.modelValue.addr_house_no ?? '',
    addr_moo:      props.modelValue.addr_moo ?? '',
    addr_road:     props.modelValue.addr_road ?? '',
    addr_tambon:   props.modelValue.addr_tambon ?? '',
    addr_amphur:   props.modelValue.addr_amphur ?? '',
    addr_province: props.modelValue.addr_province ?? '',
  }),
  set: (addr) => {
    emit('update:modelValue', {
      ...props.modelValue,
      addr_house_no: addr.addr_house_no || null,
      addr_moo:      addr.addr_moo || null,
      addr_road:     addr.addr_road || null,
      addr_tambon:   addr.addr_tambon || null,
      addr_amphur:   addr.addr_amphur || null,
      addr_province: addr.addr_province || null,
    })
  },
})
</script>

<template>
  <div class="card bg-base-100 shadow-sm">
    <div class="card-body">
      <h2 class="card-title text-base mb-2">ข้อมูลสำหรับแบบฟอร์มกู้</h2>

      <div v-if="errorMsg" class="alert alert-error text-sm mb-3">{{ errorMsg }}</div>
      <div v-if="saved" class="alert alert-success text-sm mb-3">บันทึกสำเร็จ</div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <UiInput
          label="ยศ / คำนำหน้า" size="sm" placeholder="เช่น นาย, นาง, ร.ต."
          :model-value="modelValue.title"
          @update:model-value="updateField('title', $event)"
        />
        <UiInput
          label="ตำแหน่ง" size="sm"
          :model-value="modelValue.position"
          @update:model-value="updateField('position', $event)"
        />
        <UiInput
          label="สังกัด / กรม" size="sm"
          :model-value="modelValue.department"
          @update:model-value="updateField('department', $event)"
        />
        <UiInput
          label="หน่วยงาน" size="sm"
          :model-value="modelValue.organization"
          @update:model-value="updateField('organization', $event)"
        />
        <UiInput
          label="โทรศัพท์" type="tel" size="sm"
          :model-value="modelValue.phone"
          @update:model-value="updateField('phone', $event)"
        />
      </div>

      <AddressFields
        size="sm"
        :model-value="addressModel"
        @update:model-value="addressModel = $event"
      />

      <div class="card-actions justify-end mt-4">
        <button class="btn btn-primary" :disabled="saving" @click="emit('save')">
          <span v-if="saving" class="loading loading-spinner loading-xs"></span>
          บันทึก
        </button>
      </div>
    </div>
  </div>
</template>
