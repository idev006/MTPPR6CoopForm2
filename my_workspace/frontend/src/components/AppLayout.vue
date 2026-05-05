<script setup lang="ts">
import AppSidebar from './layout/AppSidebar.vue'
import MobileTopBar from './layout/MobileTopBar.vue'
import BottomNav from './layout/BottomNav.vue'
import ConfirmDialog from './ui/ConfirmDialog.vue'
import { useToastStore } from '@/stores/toast.store'

const toast = useToastStore()
</script>

<template>
  <!-- DaisyUI drawer layout: lg:drawer-open = sidebar ถาวรบน desktop -->
  <div class="drawer lg:drawer-open min-h-screen">

    <!-- Checkbox ที่ DaisyUI ใช้ toggle drawer (ไม่ต้องใช้ Vue state) -->
    <input id="app-drawer" type="checkbox" class="drawer-toggle" />

    <!-- Main content area -->
    <div class="drawer-content flex flex-col bg-base-200">

      <!-- Mobile top bar (มีปุ่ม hamburger = label ของ drawer) -->
      <MobileTopBar />

      <!-- Page content -->
      <main class="flex-1 pb-20 lg:pb-0">
        <slot />
      </main>

      <!-- Mobile Bottom Navigation -->
      <BottomNav />

    </div>

    <!-- Sidebar panel -->
    <div class="drawer-side z-40">
      <!-- Overlay — คลิกแล้วปิด drawer (DaisyUI จัดการให้) -->
      <label for="app-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
      <AppSidebar />
    </div>

    <!-- Global Confirm Dialog -->
    <ConfirmDialog />

    <!-- Toast Notifications (fixed, ไม่เกี่ยวกับ drawer layout) -->
    <Transition name="toast">
      <div v-if="toast.visible" class="toast toast-top toast-end z-50 mt-4">
        <div
          class="alert shadow-lg border-none text-white font-bold"
          :class="{
            'alert-success bg-success': toast.type === 'success',
            'alert-error bg-error':     toast.type === 'error',
            'alert-info bg-info':       toast.type === 'info',
          }"
        >
          <span>{{ toast.message }}</span>
        </div>
      </div>
    </Transition>

  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
