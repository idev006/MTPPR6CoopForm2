<script setup lang="ts">
import { onMounted } from 'vue'
import type { Step3Data, GuarantorInfo } from '@/types/form'
import UiInput from '@/components/ui/UiInput.vue'
import AddressFields from '@/components/AddressFields.vue'

const props = defineProps<{ modelValue: Step3Data }>()
const emit = defineEmits<{ 'update:modelValue': [Step3Data] }>()

const MIN_GUARANTORS = 2
const MAX_GUARANTORS = 2

function emptyGuarantor(): GuarantorInfo {
  return {
    name: '', id_card: '', position: '', department: '', phone: '', member_code: '',
    current_addr: { house_no: '', moo: '', road: '', tambon: '', amphur: '', province: '' },
    marital_status: 'single',
    spouse_name: '',
  }
}

onMounted(() => {
  const current = props.modelValue.guarantors ?? []
  if (current.length < MIN_GUARANTORS) {
    const padded = [
      ...current,
      ...Array.from({ length: MIN_GUARANTORS - current.length }, emptyGuarantor),
    ]
    emit('update:modelValue', { guarantors: padded })
  }
})

function addGuarantor() {
  if (props.modelValue.guarantors.length >= MAX_GUARANTORS) return
  emit('update:modelValue', {
    guarantors: [...props.modelValue.guarantors, emptyGuarantor()],
  })
}

function removeGuarantor(index: number) {
  if (props.modelValue.guarantors.length <= MIN_GUARANTORS) return
  emit('update:modelValue', {
    guarantors: props.modelValue.guarantors.filter((_, i) => i !== index),
  })
}

function updateField(index: number, field: keyof GuarantorInfo, value: any) {
  const newList = [...props.modelValue.guarantors]
  newList[index] = { ...newList[index], [field]: value }
  emit('update:modelValue', { guarantors: newList })
}
</script>

<template>
  <div class="space-y-6">
    <header class="flex justify-between items-center border-b border-base-200 pb-4">
      <div>
        <h3 class="text-xl font-bold">ข้อมูลผู้ค้ำประกัน</h3>
        <p class="text-sm text-base-content/60">
          ต้องการผู้ค้ำประกันอย่างน้อย {{ MIN_GUARANTORS }} คน ไม่เกิน {{ MAX_GUARANTORS }} คน
        </p>
      </div>
      <button
        class="btn btn-primary btn-sm"
        :disabled="modelValue.guarantors.length >= MAX_GUARANTORS"
        @click="addGuarantor"
      >
        + เพิ่มผู้ค้ำประกัน
      </button>
    </header>

    <div class="grid grid-cols-1 gap-8">
      <div
        v-for="(g, idx) in modelValue.guarantors"
        :key="idx"
        class="card bg-base-100 border border-base-300 shadow-sm overflow-hidden"
      >
        <div class="bg-base-200 px-4 py-2 flex justify-between items-center">
          <span class="font-bold text-sm">ผู้ค้ำประกันคนที่ {{ idx + 1 }}</span>
          <button
            class="btn btn-ghost btn-xs text-error"
            :disabled="modelValue.guarantors.length <= MIN_GUARANTORS"
            :title="modelValue.guarantors.length <= MIN_GUARANTORS ? `ต้องมีผู้ค้ำอย่างน้อย ${MIN_GUARANTORS} คน` : ''"
            @click="removeGuarantor(idx)"
          >
            ลบออก
          </button>
        </div>

        <div class="card-body p-4 space-y-6">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <UiInput
              label="ชื่อ-นามสกุล"
              :model-value="g.name"
              @update:model-value="updateField(idx, 'name', $event)"
            />
            <UiInput
              label="เลขบัตรประชาชน" maxlength="13"
              :model-value="g.id_card"
              @update:model-value="updateField(idx, 'id_card', $event)"
            />
            <UiInput
              label="รหัสสมาชิก"
              :model-value="g.member_code"
              @update:model-value="updateField(idx, 'member_code', $event)"
            />
            <UiInput
              label="ตำแหน่ง"
              :model-value="g.position"
              @update:model-value="updateField(idx, 'position', $event)"
            />
            <UiInput
              label="สังกัด"
              :model-value="g.department"
              @update:model-value="updateField(idx, 'department', $event)"
            />
            <UiInput
              label="เบอร์โทรศัพท์"
              :model-value="g.phone"
              @update:model-value="updateField(idx, 'phone', $event)"
            />
          </div>

          <div class="bg-base-200/30 p-4 rounded-xl">
            <AddressFields
              size="sm" title="ที่อยู่ของผู้ค้ำประกัน"
              :model-value="g.current_addr"
              @update:model-value="updateField(idx, 'current_addr', $event)"
            />
          </div>

          <!-- Marital Status -->
          <div class="flex flex-wrap items-center gap-6 pt-2 border-t border-base-200">
            <div class="flex items-center gap-4">
              <span class="text-sm font-bold">สถานะ:</span>
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" :name="`marital_${idx}`" class="radio radio-primary radio-sm"
                  :checked="g.marital_status === 'single'"
                  @change="updateField(idx, 'marital_status', 'single')" />
                <span class="text-sm">โสด</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" :name="`marital_${idx}`" class="radio radio-primary radio-sm"
                  :checked="g.marital_status === 'married'"
                  @change="updateField(idx, 'marital_status', 'married')" />
                <span class="text-sm">สมรส</span>
              </label>
            </div>

            <div v-if="g.marital_status === 'married'" class="flex-1 min-w-[200px]">
              <UiInput
                label="ชื่อ-นามสกุล คู่สมรส (ผู้ค้ำประกัน)" size="sm"
                :model-value="g.spouse_name"
                @update:model-value="updateField(idx, 'spouse_name', $event)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Warning if below minimum -->
    <div v-if="modelValue.guarantors.length < MIN_GUARANTORS" class="alert alert-warning py-2 text-sm">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-5 w-5" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M12 3a9 9 0 110 18A9 9 0 0112 3z" />
      </svg>
      <span>ต้องการผู้ค้ำประกันอย่างน้อย {{ MIN_GUARANTORS }} คน (ปัจจุบัน {{ modelValue.guarantors.length }} คน)</span>
    </div>
  </div>
</template>
