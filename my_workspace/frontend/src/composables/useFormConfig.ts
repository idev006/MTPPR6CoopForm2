import { ref, computed } from 'vue'
import { formConfigService, type FormConfig, type StepDef } from '@/services/form.config.service'
import { useAuthStore } from '@/stores/auth.store'

export function useFormConfig(formId: string) {
  const auth = useAuthStore()
  const config = ref<FormConfig | null>(null)
  const loading = ref(false)
  const error = ref('')

  const steps = computed<StepDef[]>(() => {
    if (!config.value) return []
    return config.value.steps.filter(step =>
      step.roles.length === 0 || step.roles.some(r => auth.hasRole(r))
    )
  })

  async function load() {
    loading.value = true
    error.value = ''
    try {
      config.value = await formConfigService.get(formId)
    } catch {
      error.value = `ไม่สามารถโหลดคอนฟิกฟอร์ม '${formId}' ได้`
    } finally {
      loading.value = false
    }
  }

  return { config, steps, loading, error, load }
}
