import { defineStore } from 'pinia'
import { ref, reactive, computed, watch } from 'vue'
import { draftService } from '@/services/draft.service'
import type { DraftSession } from '@/types/draft'
import type {
  Step1Data, Step2Data, Step3Data, Step4Data, Step5Data, Step6Data,
  StepEmergencyData,
  LoanOrdinaryFormData, LoanEmergencyFormData, AddressInfo, SignatureData
} from '@/types/form'

const AUTO_SAVE_DELAY = 30_000

// ─── helpers ────────────────────────────────────────────
function emptyAddr(): AddressInfo {
  return { house_no: '', moo: '', road: '', tambon: '', amphur: '', province: '' }
}
function emptyStep1(): Step1Data {
  return {
    title: '', first_name: '', last_name: '', id_card: '', position: '', department: '', organization: '', phone: '', member_code: '',
    marital_status: 'single',
    spouse_name: '',
    current_addr: emptyAddr(),
    register_addr: emptyAddr(),
    salary: null, shares_amount: null, existing_debt: null
  }
}
function emptyStep2(): Step2Data {
  return { loan_amount: null, loan_purpose: '', repayment_period: null, payout_method: 'transfer' }
}
function emptyStep3(): Step3Data {
  return { guarantors: [] }
}
function emptySig(): SignatureData {
  return { signed: false }
}
function emptyStep4(): Step4Data {
  return {
    borrower_sig: emptySig(),
    spouse_sig: emptySig(),
    guarantor_sigs: [],
    guarantor_spouse_sigs: [],
    superior_sig: emptySig(),
    superior_opinion: null
  }
}
function emptyStep5(): Step5Data {
  return { checklist_items: Array(18).fill(false), limit_analysis: { total_income: 0, total_deduction: 0, net_income: 0 } }
}
function emptyStep6(): Step6Data {
  return {
    contract_no: '', interest_rate: 0, effective_date: '',
    manager_sig: emptySig(), chairman_sig: emptySig(),
    witness_sig_1: emptySig(), witness_sig_2: emptySig(),
    manager_name: '', chairman_name: '', witness_1_name: '', witness_2_name: '',
  }
}
function emptyEmergency(): StepEmergencyData {
  return { loan_amount: null, loan_purpose: '', repayment_period: null, payout_method: 'transfer' }
}

// ────────────────────────────────────────────────────────
export const useFormStore = defineStore('form', () => {
  const draftId    = ref<string | null>(null)
  const formType   = ref('loan_ordinary')
  const currentTab = ref(0)
  const isDirty    = ref(false)
  const submitting = ref(false)
  const submitError = ref('')
  const validationErrors = ref<Record<string, string>>({})
  const submissionResult = ref<{ application_no: string; application_id: string } | null>(null)
  
  const pdfViewed = ref(false)

  const saving    = ref(false)
  const lastSaved = ref<Date | null>(null)
  const saveError = ref('')

  const step1 = reactive<Step1Data>(emptyStep1())
  const step2 = reactive<Step2Data>(emptyStep2())
  const stepEmergency = reactive<StepEmergencyData>(emptyEmergency())
  const step3 = reactive<Step3Data>(emptyStep3())
  const step4 = reactive<Step4Data>(emptyStep4())
  const step5 = reactive<Step5Data>(emptyStep5())
  const step6 = reactive<Step6Data>(emptyStep6())

  const formData = computed<LoanOrdinaryFormData | LoanEmergencyFormData>(() => {
    if (formType.value === 'loan_emergency') {
      return {
        step1: { ...step1 },
        step2: { ...stepEmergency },
        step4: { ...step4 },
      } as LoanEmergencyFormData
    }
    return {
      step1: { ...step1 },
      step2: { ...step2 },
      step3: { ...step3 },
      step4: { ...step4 },
      step5: { ...step5 },
      step6: { ...step6 },
    } as LoanOrdinaryFormData
  })

  let autoSaveTimer: ReturnType<typeof setTimeout> | null = null
  watch(isDirty, (dirty) => {
    if (!dirty) return
    if (autoSaveTimer) clearTimeout(autoSaveTimer)
    autoSaveTimer = setTimeout(() => { if (isDirty.value) save() }, AUTO_SAVE_DELAY)
  })

  function initFromDraft(draft: DraftSession) {
    draftId.value    = draft.id
    currentTab.value = Math.max((draft.current_step ?? 1) - 1, 0)
    formType.value   = draft.form_type

    const d = draft.form_data as any
    if (d.step1) {
      Object.assign(step1, d.step1)
      // Normalize: old drafts may have null address fields
      if (!step1.current_addr)  step1.current_addr  = emptyAddr()
      if (!step1.register_addr) step1.register_addr = emptyAddr()
    }

    if (formType.value === 'loan_emergency') {
      if (d.step2) Object.assign(stepEmergency, d.step2)
    } else {
      if (d.step2) Object.assign(step2, d.step2)
      if (d.step3) {
        Object.assign(step3, d.step3)
        // Normalize: old drafts stored guarantor address as "address", now "current_addr"
        step3.guarantors = step3.guarantors.map((g: any) => ({
          ...g,
          current_addr: g.current_addr ?? g.address ?? emptyAddr(),
        }))
      }
      if (d.step5) Object.assign(step5, d.step5)
      if (d.step6) Object.assign(step6, d.step6)
    }

    if (d.step4) Object.assign(step4, d.step4)
    isDirty.value = false
  }

  async function save(): Promise<void> {
    const toast = await import('@/stores/toast.store').then(m => m.useToastStore())
    if (!draftId.value) {
      await startNewDraft()
      return
    }
    saveError.value = ''; saving.value = true
    try {
      await draftService.update(draftId.value, { form_data: formData.value, current_step: currentTab.value + 1 })
      isDirty.value = false; lastSaved.value = new Date()
      toast.show('บันทึกร่างสำเร็จแล้ว')
    } catch { 
      saveError.value = 'บันทึกไม่สำเร็จ'
      toast.show('ไม่สามารถบันทึกร่างได้', 'error')
    } finally { saving.value = false }
  }

  async function startNewDraft(): Promise<void> {
    const toast = await import('@/stores/toast.store').then(m => m.useToastStore())
    saving.value = true
    try {
      const draft = await draftService.createOrGet(formType.value)
      draftId.value = draft.id
      lastSaved.value = new Date()
      isDirty.value = false
      toast.show('เริ่มร่างคำขอใหม่แล้ว')
    } catch {
      saveError.value = 'ไม่สามารถสร้างร่างคำขอได้'
      toast.show('ไม่สามารถสร้างร่างคำขอได้', 'error')
    } finally {
      saving.value = false
    }
  }

  async function validateForm() {
    const { ordinaryLoanSchema, emergencyLoanSchema } = await import('@/schemas/validation')
    validationErrors.value = {}
    
    const schema = formType.value === 'loan_emergency' ? emergencyLoanSchema : ordinaryLoanSchema
    const result = schema.safeParse(formData.value)
    
    if (!result.success) {
      result.error.errors.forEach(err => {
        validationErrors.value[err.path.join('.')] = err.message
      })
      return false
    }
    return true
  }

  async function submitForm() {
    const isValid = await validateForm()
    if (!isValid) {
      submitError.value = 'กรุณาตรวจสอบความถูกต้องของข้อมูล'
      return false
    }

    const { applicationService } = await import('@/services/application.service')
    submitting.value = true
    submitError.value = ''
    const toast = await import('@/stores/toast.store').then(m => m.useToastStore())
    try {
      const res = await applicationService.submit(formData.value, formType.value, draftId.value)
      if (res.success) {
        submissionResult.value = { application_no: res.application_no, application_id: res.application_id }
        // ลบ draft หลัง submit สำเร็จ — silent fail ถ้า backend ไม่ตอบสนอง
        if (draftId.value) {
          try { await draftService.delete(draftId.value) } catch { /* intentional */ }
          draftId.value = null
        }
        toast.show('ส่งคำขอเรียบร้อยแล้ว')
        return true
      }
      return false
    } catch (err: any) {
      submitError.value = err.response?.data?.detail || 'การส่งข้อมูลล้มเหลว'
      toast.show(submitError.value, 'error')
      return false
    } finally {
      submitting.value = false
    }
  }

  function markDirty() { isDirty.value = true }
  function setTab(idx: number) { currentTab.value = idx }
  function setPdfViewed() { pdfViewed.value = true }

  // Generic step accessors — used by GenericFormWizard
  const _stepMap: Record<string, any> = { step1, step2, stepEmergency, step3, step4, step5, step6 }
  const _updateMap: Record<string, (v: any) => void> = {
    step1: updateStep1, step2: updateStep2, stepEmergency: updateStepEmergency,
    step3: updateStep3, step4: updateStep4, step5: updateStep5, step6: updateStep6,
  }
  function getStep(key: string): any { return _stepMap[key] ?? null }
  function setStep(key: string, value: any): void { _updateMap[key]?.(value) }

  // Pre-fill step1 จาก profile — เรียกเฉพาะเมื่อสร้าง draft ใหม่ (step1 ยังว่าง)
  function prefillStep1IfEmpty(data: Partial<Step1Data>) {
    if (step1.first_name || step1.last_name || step1.member_code) return
    Object.assign(step1, data)
  }

  function updateStep1(data: Step1Data) { Object.assign(step1, data); markDirty() }
  function updateStep2(data: Step2Data) { Object.assign(step2, data); markDirty() }
  function updateStep3(data: Step3Data) { Object.assign(step3, data); markDirty() }
  function updateStep4(data: Step4Data) { Object.assign(step4, data); markDirty() }
  function updateStep5(data: Step5Data) { Object.assign(step5, data); markDirty() }
  function updateStep6(data: Step6Data) { Object.assign(step6, data); markDirty() }
  function updateStepEmergency(data: StepEmergencyData) { Object.assign(stepEmergency, data); markDirty() }

  function reset() {
    if (autoSaveTimer) { clearTimeout(autoSaveTimer); autoSaveTimer = null }
    draftId.value = null; currentTab.value = 0; isDirty.value = false; lastSaved.value = null; saveError.value = ''
    submissionResult.value = null; submitError.value = ''; validationErrors.value = {}; pdfViewed.value = false
    Object.assign(step1, emptyStep1()); Object.assign(step2, emptyStep2())
    Object.assign(stepEmergency, emptyEmergency())
    Object.assign(step3, emptyStep3()); Object.assign(step4, emptyStep4())
    Object.assign(step5, emptyStep5()); Object.assign(step6, emptyStep6())
  }

  return {
    draftId, formType, currentTab, isDirty, saving, lastSaved, saveError,
    submitting, submitError, validationErrors, submissionResult, pdfViewed,
    step1, step2, stepEmergency, step3, step4, step5, step6, formData,
    initFromDraft, save, startNewDraft, markDirty, setTab, setPdfViewed, prefillStep1IfEmpty, submitForm, validateForm,
    updateStep1, updateStep2, updateStepEmergency, updateStep3, updateStep4, updateStep5, updateStep6, reset,
    getStep, setStep,
  }
})
