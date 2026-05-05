<script setup lang="ts">
import EmergencyLoanWizard from '@/forms/emergency-loan/EmergencyLoanWizard.vue'
import AppLayout from '@/components/AppLayout.vue'
import { useFormStore } from '@/stores/form.store'
import { useProfileStore } from '@/stores/profile.store'
import { draftService } from '@/services/draft.service'
import { onMounted } from 'vue'

const form = useFormStore()
const profile = useProfileStore()

onMounted(async () => {
  form.formType = 'loan_emergency'

  await profile.fetch()

  const existing = await draftService.getByFormType('loan_emergency')
  if (existing) {
    form.initFromDraft(existing)
  } else {
    await form.startNewDraft()
    form.prefillStep1IfEmpty(profile.step1Prefill)
  }
})
</script>

<template>
  <AppLayout>
    <div class="max-w-5xl mx-auto p-4 md:p-8">
      <header class="mb-8">
        <h1 class="text-3xl font-black uppercase tracking-tight text-secondary">ยื่นคำขอกู้เงินฉุกเฉิน</h1>
        <p class="text-base-content/50 font-bold text-sm">บรรเทาความเดือดร้อนเร่งด่วน วงเงินสูงสุด 50,000 บาท</p>
      </header>

      <EmergencyLoanWizard />
    </div>
  </AppLayout>
</template>
