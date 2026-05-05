<script setup lang="ts">
import type { GuarantorInfo } from '@/types/form'
import UiInput from '@/components/ui/UiInput.vue'

const props = defineProps<{ modelValue: GuarantorInfo; index: number }>()
const emit = defineEmits<{ 'update:modelValue': [GuarantorInfo] }>()

function update(field: keyof GuarantorInfo, value: string) {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
}
</script>

<template>
  <div class="card bg-base-200">
    <div class="card-body py-4">
      <h4 class="font-semibold text-sm">ผู้ค้ำประกันคนที่ {{ index }}</h4>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-2">
        <div class="sm:col-span-2">
          <UiInput label="ชื่อ-สกุล" size="sm" :required="true"
            :model-value="modelValue.name" @update:model-value="update('name', $event)" />
        </div>
        <UiInput label="ตำแหน่ง" size="sm" :required="true"
          :model-value="modelValue.position" @update:model-value="update('position', $event)" />
        <UiInput label="สังกัด" size="sm"
          :model-value="modelValue.department" @update:model-value="update('department', $event)" />
        <UiInput label="โทรศัพท์" type="tel" size="sm"
          :model-value="modelValue.phone" @update:model-value="update('phone', $event)" />
      </div>
    </div>
  </div>
</template>
