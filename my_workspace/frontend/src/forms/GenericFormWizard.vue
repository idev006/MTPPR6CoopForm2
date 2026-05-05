<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useFormStore } from '@/stores/form.store'
import { useAuthStore } from '@/stores/auth.store'
import { ROLES } from '@/constants/roles'
import { useFormConfig } from '@/composables/useFormConfig'
import { resolveComponent } from '@/forms/registry'
import BaseWizardLayout from '@/forms/shared/BaseWizardLayout.vue'

const props = defineProps<{ formId: string }>()

const auth = useAuthStore()
const form = useFormStore()
const { steps, loading, error, load } = useFormConfig(props.formId)

onMounted(() => load())

const safeTabIndex = computed(() =>
  Math.min(Math.max(form.currentTab, 0), steps.value.length - 1)
)

const currentStep = computed(() => steps.value[safeTabIndex.value] ?? null)

const currentComponent = computed(() => {
  if (!currentStep.value) return null
  return resolveComponent(currentStep.value.component)
})

const currentStepData = computed(() => {
  const key = currentStep.value?.store_key
  if (!key) return null
  return form.getStep(key)
})

function handleUpdate(value: any) {
  const key = currentStep.value?.store_key
  if (!key) return
  form.setStep(key, value)
}

const lastSavedText = computed(() => {
  if (!form.lastSaved) return ''
  return `บันทึกอัตโนมัติ ${form.lastSaved.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })}`
})
</script>

<template>
  <div v-if="loading" class="flex justify-center items-center h-64">
    <span class="loading loading-spinner loading-lg"></span>
  </div>

  <div v-else-if="error" class="alert alert-error">{{ error }}</div>

  <BaseWizardLayout
    v-else
    :tabs="steps"
    :current-tab="safeTabIndex"
    :saving="form.saving"
    :save-error="form.saveError"
    :last-saved-text="lastSavedText"
    :is-dirty="form.isDirty"
    :submitting="form.submitting"
    :submit-error="form.submitError"
    :can-submit="auth.hasRole(ROLES.BORROWER)"
    @set-tab="form.setTab"
    @save="form.save"
    @submit="form.submitForm"
    @prev="form.setTab(form.currentTab - 1)"
    @next="form.setTab(form.currentTab + 1)"
  >
    <component
      v-if="currentComponent"
      :is="currentComponent"
      :model-value="currentStepData"
      @update:model-value="handleUpdate"
    />
  </BaseWizardLayout>
</template>
