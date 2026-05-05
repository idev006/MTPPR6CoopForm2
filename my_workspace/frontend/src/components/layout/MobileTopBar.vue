<template>
  <div class="lg:hidden flex items-center justify-between px-4 py-3 bg-base-100 border-b border-base-300 sticky top-0 z-30">
    <div class="flex items-center gap-2">
      <!-- Hamburger = label ของ DaisyUI drawer checkbox (ไม่ต้อง emit) -->
      <label
        for="app-drawer"
        class="btn btn-ghost btn-sm btn-circle"
        aria-label="เปิดเมนู"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </label>
      <span class="text-xl">🏦</span>
      <span class="font-bold text-base">CoopForm</span>
    </div>
    <div class="flex items-center gap-1">
      <NotificationBell />
      <ThemePicker />
    </div>
  </div>
</template>

<script setup lang="ts">
import NotificationBell from './NotificationBell.vue'
import ThemePicker from '@/components/ThemePicker.vue'
// ไม่ต้องใช้ emit แล้ว — DaisyUI drawer ใช้ label/checkbox แทน
</script>
