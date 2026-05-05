import { ref } from 'vue'
import { defineStore } from 'pinia'

interface ConfirmOptions {
  title?: string
  confirmLabel?: string
  confirmClass?: string  // DaisyUI btn class เช่น 'btn-error', 'btn-warning'
}

export const useConfirmStore = defineStore('confirm', () => {
  const visible  = ref(false)
  const message  = ref('')
  const title    = ref('ยืนยันการดำเนินการ')
  const confirmLabel = ref('ยืนยัน')
  const confirmClass = ref('btn-error')

  let resolver: ((val: boolean) => void) | null = null

  /**
   * เปิด confirm dialog และ return Promise<boolean>
   * await confirm('ต้องการลบใช่ไหม?') → true = กด ยืนยัน, false = กด ยกเลิก
   */
  function confirm(msg: string, opts: ConfirmOptions = {}): Promise<boolean> {
    message.value      = msg
    title.value        = opts.title        ?? 'ยืนยันการดำเนินการ'
    confirmLabel.value = opts.confirmLabel ?? 'ยืนยัน'
    confirmClass.value = opts.confirmClass ?? 'btn-error'
    visible.value      = true

    return new Promise((resolve) => {
      resolver = resolve
    })
  }

  function accept() {
    visible.value = false
    resolver?.(true)
    resolver = null
  }

  function cancel() {
    visible.value = false
    resolver?.(false)
    resolver = null
  }

  return { visible, message, title, confirmLabel, confirmClass, confirm, accept, cancel }
})
