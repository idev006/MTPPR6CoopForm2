<script setup lang="ts">
import type { AddressInfo } from '@/types/form'
import UiInput from './ui/UiInput.vue'

const props = defineProps<{ 
  modelValue: AddressInfo; 
  size?: 'sm' | 'md';
  title?: string;
}>()
const emit = defineEmits<{ 'update:modelValue': [AddressInfo] }>()

function update(field: keyof AddressInfo, value: string) {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
}
</script>

<template>
  <div class="space-y-4">
    <div v-if="title" class="divider text-xs font-bold uppercase tracking-wider text-base-content/40 my-2">{{ title }}</div>
    <div v-if="modelValue" class="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <UiInput
        label="บ้านเลขที่" :required="true" :size="size"
        :model-value="modelValue.house_no"
        @update:model-value="update('house_no', $event)"
      />
      <UiInput
        label="หมู่ที่" :size="size"
        :model-value="modelValue.moo"
        @update:model-value="update('moo', $event)"
      />
      <UiInput
        label="ถนน" :size="size"
        :model-value="modelValue.road"
        @update:model-value="update('road', $event)"
      />
      <UiInput
        label="ตำบล / แขวง" :required="true" :size="size"
        :model-value="modelValue.tambon"
        @update:model-value="update('tambon', $event)"
      />
      <UiInput
        label="อำเภอ / เขต" :required="true" :size="size"
        :model-value="modelValue.amphur"
        @update:model-value="update('amphur', $event)"
      />
      <UiInput
        label="จังหวัด" :required="true" :size="size"
        :model-value="modelValue.province"
        @update:model-value="update('province', $event)"
      />
    </div>
  </div>
</template>
