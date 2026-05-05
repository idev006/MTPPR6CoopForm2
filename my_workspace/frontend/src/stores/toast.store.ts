import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const message = ref('')
  const type = ref<'success' | 'error' | 'info'>('info')
  const visible = ref(false)
  let timer: ReturnType<typeof setTimeout> | null = null

  function show(msg: string, t: 'success' | 'error' | 'info' = 'success') {
    message.value = msg
    type.value = t
    visible.value = true
    
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      visible.value = false
    }, 3000)
  }

  return { message, type, visible, show }
})
