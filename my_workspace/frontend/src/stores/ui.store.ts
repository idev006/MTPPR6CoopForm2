import { defineStore } from 'pinia'
import { ref } from 'vue'

type AlertType = 'success' | 'error' | 'warning' | 'info'

interface Alert {
  id: number
  type: AlertType
  message: string
}

const STORAGE_KEY = 'coopform-theme'
const DEFAULT_THEME = 'light'

export const THEMES = [
  'light', 'dark', 'cupcake', 'bumblebee', 'emerald', 'corporate',
  'synthwave', 'retro', 'cyberpunk', 'valentine', 'halloween', 'garden',
  'forest', 'aqua', 'lofi', 'pastel', 'fantasy', 'wireframe', 'black',
  'luxury', 'dracula', 'cmyk', 'autumn', 'business', 'acid', 'lemonade',
  'night', 'coffee', 'winter', 'dim', 'nord', 'sunset',
] as const

export type Theme = typeof THEMES[number]

export const useUiStore = defineStore('ui', () => {
  const isLoading = ref(false)
  const alerts = ref<Alert[]>([])
  let alertCounter = 0

  const savedTheme = localStorage.getItem(STORAGE_KEY) as Theme | null
  const theme = ref<Theme>(
    savedTheme && (THEMES as readonly string[]).includes(savedTheme)
      ? savedTheme
      : DEFAULT_THEME,
  )

  function setTheme(t: Theme) {
    theme.value = t
    localStorage.setItem(STORAGE_KEY, t)
    document.documentElement.setAttribute('data-theme', t)
  }

  function initTheme() {
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  function setLoading(val: boolean) {
    isLoading.value = val
  }

  function addAlert(type: AlertType, message: string, durationMs = 4000) {
    const id = ++alertCounter
    alerts.value.push({ id, type, message })
    setTimeout(() => removeAlert(id), durationMs)
  }

  function removeAlert(id: number) {
    alerts.value = alerts.value.filter((a) => a.id !== id)
  }

  return { isLoading, alerts, theme, setTheme, initTheme, setLoading, addAlert, removeAlert }
})
