import type { Component } from 'vue'

import Step1PersonalInfo from '@/forms/shared/Step1PersonalInfo.vue'
import StepEmergencyDetails from '@/forms/emergency-loan/StepEmergencyDetails.vue'
import StepAttachments from '@/forms/shared/StepAttachments.vue'
import Step4SignatureHub from '@/forms/shared/Step4SignatureHub.vue'
import Step2LoanDetails from '@/forms/ordinary-loan/Step2LoanDetails.vue'
import Step3Guarantors from '@/forms/ordinary-loan/Step3Guarantors.vue'
import Step5StaffVerification from '@/forms/staff/Step5StaffVerification.vue'
import Step6ContractFinalization from '@/forms/staff/Step6ContractFinalization.vue'

// Maps TOML component name → actual Vue component
// เพิ่ม entry ที่นี่เมื่อมี step component ใหม่
export const COMPONENT_REGISTRY: Record<string, Component> = {
  Step1PersonalInfo,
  StepEmergencyDetails,
  StepAttachments,
  Step4SignatureHub,
  Step2LoanDetails,
  Step3Guarantors,
  Step5StaffVerification,
  Step6ContractFinalization,
}

export function resolveComponent(name: string): Component | null {
  return COMPONENT_REGISTRY[name] ?? null
}
