<template>
  <!-- DaisyUI dialog modal — Teleport ไป body เพื่อไม่ติด z-index ของ parent -->
  <Teleport to="body">
    <dialog
      class="modal"
      :class="{ 'modal-open': confirmStore.visible }"
    >
      <div class="modal-box max-w-sm">
        <!-- Title -->
        <h3 class="font-bold text-lg">{{ confirmStore.title }}</h3>

        <!-- Message -->
        <p class="py-4 text-base-content/80 text-sm leading-relaxed whitespace-pre-wrap">
          {{ confirmStore.message }}
        </p>

        <!-- Actions -->
        <div class="modal-action">
          <button class="btn btn-ghost" @click="confirmStore.cancel()">
            ยกเลิก
          </button>
          <button
            class="btn"
            :class="confirmStore.confirmClass"
            @click="confirmStore.accept()"
          >
            {{ confirmStore.confirmLabel }}
          </button>
        </div>
      </div>

      <!-- backdrop คลิกแล้วปิด (= ยกเลิก) -->
      <form method="dialog" class="modal-backdrop">
        <button @click="confirmStore.cancel()">close</button>
      </form>
    </dialog>
  </Teleport>
</template>

<script setup lang="ts">
import { useConfirmStore } from '@/stores/confirm.store'
const confirmStore = useConfirmStore()
</script>
