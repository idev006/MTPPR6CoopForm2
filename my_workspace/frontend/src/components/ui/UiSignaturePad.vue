<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import SignaturePad from 'signature_pad'

interface Props {
  title?: string
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'ลงชื่อยืนยัน',
  placeholder: 'กรุณาเซ็นชื่อภายในกรอบนี้'
})

const emit = defineEmits<{
  (e: 'save', data: string): void
  (e: 'cancel'): void
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const signatureError = ref('')   // inline error แทน alert()
let signaturePad: SignaturePad | null = null

function resizeCanvas() {
  if (!canvasRef.value) return
  const canvas = canvasRef.value
  const ratio = Math.max(window.devicePixelRatio || 1, 1)
  canvas.width = canvas.offsetWidth * ratio
  canvas.height = canvas.offsetHeight * ratio
  canvas.getContext('2d')?.scale(ratio, ratio)
  signaturePad?.clear()
}

onMounted(() => {
  if (canvasRef.value) {
    signaturePad = new SignaturePad(canvasRef.value, {
      backgroundColor: 'rgb(255, 255, 255)',
      penColor: 'rgb(0, 0, 0)'
    })
    // ล้าง error เมื่อผู้ใช้เริ่มเซ็น
    signaturePad.addEventListener('beginStroke', () => { signatureError.value = '' })
    window.addEventListener('resize', resizeCanvas)
    resizeCanvas()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCanvas)
})

function clear() {
  signaturePad?.clear()
  signatureError.value = ''
}

function save() {
  if (signaturePad?.isEmpty()) {
    signatureError.value = 'กรุณาเซ็นชื่อในกรอบก่อนกดยืนยัน'
    return
  }
  const data = signaturePad?.toDataURL('image/png')
  if (data) emit('save', data)
}
</script>

<template>
  <div class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
    <div class="bg-base-100 w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">

      <!-- Header -->
      <div class="p-4 border-b border-base-200 flex justify-between items-center bg-base-200/50">
        <h3 class="font-bold text-lg text-primary">{{ props.title }}</h3>
        <button class="btn btn-ghost btn-sm btn-circle" @click="emit('cancel')">✕</button>
      </div>

      <!-- Canvas Area -->
      <div class="p-4 flex-1 flex flex-col gap-2 min-h-[300px]">
        <p class="text-xs text-base-content/50 italic text-center">{{ props.placeholder }}</p>
        <div
          class="flex-1 border-2 border-dashed rounded-xl relative bg-white overflow-hidden transition-colors"
          :class="signatureError ? 'border-error' : 'border-base-300'"
        >
          <canvas ref="canvasRef" class="w-full h-full touch-none cursor-crosshair"></canvas>
        </div>

        <!-- Inline error — แทน alert() -->
        <Transition name="fade">
          <div v-if="signatureError" class="alert alert-error py-2 text-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            </svg>
            {{ signatureError }}
          </div>
        </Transition>
      </div>

      <!-- Actions -->
      <div class="p-4 bg-base-200/30 flex justify-between items-center gap-2">
        <button class="btn btn-ghost" @click="clear">ล้างใหม่</button>
        <div class="flex gap-2">
          <button class="btn btn-outline" @click="emit('cancel')">ยกเลิก</button>
          <button class="btn btn-primary px-8" @click="save">ยืนยันลายเซ็น</button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
canvas {
  display: block;
  width: 100% !important;
  height: 100% !important;
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
