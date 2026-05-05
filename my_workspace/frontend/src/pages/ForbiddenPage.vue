<template>
  <div class="min-h-screen bg-base-200 flex items-center justify-center p-4">
    <div class="text-center max-w-md">
      <div class="text-8xl font-bold text-base-300 mb-4">403</div>
      <h1 class="text-2xl font-bold text-base-content mb-2">ไม่มีสิทธิ์เข้าถึง</h1>
      <p class="text-base-content/60 mb-8">
        คุณไม่มีสิทธิ์เข้าถึงหน้านี้ กรุณาติดต่อผู้ดูแลระบบ
      </p>
      <div class="flex gap-3 justify-center">
        <button class="btn btn-ghost" @click="router.back()">
          ← ย้อนกลับ
        </button>
        <RouterLink :to="homeRoute" class="btn btn-primary">
          ไปหน้าหลัก
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

const router = useRouter()
const auth = useAuthStore()

const homeRoute = computed(() =>
  auth.user?.role === 'staff' ? '/staff' : '/'
)
</script>
