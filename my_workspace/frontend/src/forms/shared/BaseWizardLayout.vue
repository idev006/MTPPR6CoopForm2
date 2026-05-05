<script setup lang="ts">
import { computed } from 'vue'
import { useFormStore } from '@/stores/form.store'

interface TabDef {
  label: string
}

const props = defineProps<{
  tabs: TabDef[]
  currentTab: number
  saving?: boolean
  saveError?: string
  lastSavedText?: string
  isDirty?: boolean
  submitting?: boolean
  submitError?: string
  canSubmit?: boolean
}>()

const emit = defineEmits(['setTab', 'save', 'submit', 'prev', 'next'])

const isDev = import.meta.env.DEV

async function fillDummyData() {
  const { dummyStep1, dummyStep2, dummyStep3, dummyStep4, dummyStep5, dummyStep6 } =
    await import('@/dev/dummyData')
  const form = useFormStore()
  form.updateStep1(dummyStep1)
  form.updateStep2(dummyStep2)
  form.updateStep3(dummyStep3)
  form.updateStep4(dummyStep4)
  form.updateStep5(dummyStep5)
  form.updateStep6(dummyStep6)
}

const isFirstTab = computed(() => props.currentTab === 0)
const isLastTab = computed(() => props.currentTab === props.tabs.length - 1)
</script>

<template>
  <div class="w-full">
    <!-- Tabs nav -->
    <div class="overflow-x-auto pb-1 mb-0">
      <div role="tablist" class="tabs tabs-border tabs-md min-w-max">
        <a
          v-for="(tab, idx) in tabs"
          :key="idx"
          role="tab"
          class="tab whitespace-nowrap"
          :class="{ 'tab-active': currentTab === idx }"
          @click="emit('setTab', idx)"
        >
          {{ tab.label }}
        </a>
      </div>
    </div>

    <!-- Status Bar -->
    <div class="flex justify-between items-center py-2 px-1 h-8">
      <div>
        <button
          v-if="isDev"
          class="btn btn-xs btn-warning gap-1 opacity-70 hover:opacity-100"
          title="เติมข้อมูลทดสอบ (Dev only)"
          @click="fillDummyData"
        >
          🧪 เติมข้อมูลทดสอบ
        </button>
      </div>
      <div class="flex items-center gap-2 text-[10px] text-base-content/40 uppercase tracking-wider">
        <span v-if="saving" class="loading loading-spinner loading-xs"></span>
        <span class="text-error" v-if="saveError">{{ saveError }}</span>
        <span v-else-if="lastSavedText">{{ saving ? 'Saving...' : lastSavedText }}</span>
      </div>
    </div>

    <!-- Main Content -->
    <div class="card bg-base-100 shadow-sm border border-base-200">
      <div class="card-body p-4 md:p-8">
        <slot></slot>
      </div>
    </div>

    <!-- Navigation -->
    <div class="flex justify-between items-center mt-6">
      <button
        class="btn btn-ghost btn-sm px-4"
        :disabled="isFirstTab"
        @click="emit('prev')"
      >
        ← ย้อนกลับ
      </button>
      
      <div class="flex gap-2">
        <button
          class="btn btn-outline btn-sm px-4"
          :disabled="saving || !isDirty"
          @click="emit('save')"
        >
          บันทึกร่าง
        </button>
        
        <button
          v-if="!isLastTab"
          class="btn btn-primary btn-sm px-6"
          @click="emit('next')"
        >
          ถัดไป →
        </button>
        
        <button
          v-else
          class="btn btn-success btn-sm px-6 text-white"
          :disabled="submitting || saving || !canSubmit"
          @click="emit('submit')"
        >
          <span v-if="submitting" class="loading loading-spinner loading-xs"></span>
          ส่งคำขอรับพิจารณา
        </button>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="submitError" class="alert alert-error shadow-sm mt-4 py-2 text-sm text-white border-none rounded-lg">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-5 w-5" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
      <span>{{ submitError }}</span>
    </div>
  </div>
</template>
