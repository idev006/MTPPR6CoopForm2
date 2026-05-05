<script setup lang="ts">
import { useAuthStore } from '@/stores/auth.store'

const auth = useAuthStore()
</script>

<template>
  <div class="card bg-base-100 shadow-sm">
    <div class="card-body">
      <h2 class="card-title text-base">ข้อมูลบัญชี</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
        <div>
          <p class="text-base-content/60">ชื่อ-สกุล</p>
          <p class="font-medium">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</p>
        </div>
        <div>
          <p class="text-base-content/60">อีเมล</p>
          <p class="font-medium">{{ auth.user?.email }}</p>
        </div>
        <div v-if="auth.user?.member_code">
          <p class="text-base-content/60">รหัสสมาชิก</p>
          <p class="font-medium">{{ auth.user.member_code }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
