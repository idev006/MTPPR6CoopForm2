<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import OrdinaryLoanWizard from '@/forms/ordinary-loan/OrdinaryLoanWizard.vue'
import AppLayout from '@/components/AppLayout.vue'
import { useFormStore } from '@/stores/form.store'
import { useProfileStore } from '@/stores/profile.store'
import { draftService } from '@/services/draft.service'

const form = useFormStore()
const profile = useProfileStore()
const router = useRouter()

const showSuccess = ref(false)

onMounted(async () => {
  form.formType = 'loan_ordinary'

  await profile.fetch()

  const existing = await draftService.getByFormType('loan_ordinary')
  if (existing) {
    form.initFromDraft(existing)
  } else {
    await form.startNewDraft()
    form.prefillStep1IfEmpty(profile.step1Prefill)
  }
})

watch(() => form.submissionResult, (result) => {
  if (result) showSuccess.value = true
})

function goToDashboard() {
  form.reset()
  router.push({ name: 'dashboard' })
}
</script>

<template>
  <AppLayout>
    <div class="max-w-5xl mx-auto p-4 md:p-8">
      <header class="mb-8">
        <h1 class="text-3xl font-black text-primary uppercase tracking-tight">ยื่นคำขอกู้เงินสามัญ</h1>
        <p class="text-base-content/50 font-bold text-sm">กรุณากรอกข้อมูลให้ครบถ้วนทุกขั้นตอน</p>
      </header>

      <OrdinaryLoanWizard />
    </div>

    <!-- Success Modal -->
    <div v-if="showSuccess" class="modal modal-open">
      <div class="modal-box max-w-md text-center">
        <!-- Checkmark icon -->
        <div class="flex justify-center mb-4">
          <div class="w-20 h-20 rounded-full bg-success/10 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-success" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>

        <h2 class="text-2xl font-bold text-base-content mb-2">ส่งคำขอสำเร็จแล้ว!</h2>
        <p class="text-base-content/60 text-sm mb-6">ระบบได้รับคำขอกู้เงินสามัญของท่านเรียบร้อยแล้ว</p>

        <!-- Application number -->
        <div class="bg-base-200 rounded-lg p-4 mb-4">
          <p class="text-xs text-base-content/50 uppercase tracking-wide mb-1">หมายเลขคำขอ</p>
          <p class="text-2xl font-mono font-bold text-primary">
            {{ form.submissionResult?.application_no }}
          </p>
        </div>

        <p class="text-sm text-base-content/60 mb-8">
          เจ้าหน้าที่จะตรวจสอบคำขอของท่านและติดต่อกลับภายใน 3–5 วันทำการ
          กรุณาเก็บหมายเลขคำขอนี้ไว้เป็นหลักฐาน
        </p>

        <button class="btn btn-primary w-full" @click="goToDashboard">
          ไปยังหน้าหลัก
        </button>
      </div>
    </div>
  </AppLayout>
</template>
