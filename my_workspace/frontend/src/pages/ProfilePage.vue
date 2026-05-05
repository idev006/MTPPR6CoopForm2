<script setup lang="ts">
import { reactive, watch, onMounted } from 'vue'
import { useProfileStore } from '@/stores/profile.store'
import AppLayout from '@/components/AppLayout.vue'
import ProfileAccountCard from '@/components/ProfileAccountCard.vue'
import ProfileEditCard from '@/components/ProfileEditCard.vue'
import type { MemberProfileUpdate } from '@/types/member'

const profileStore = useProfileStore()

const form = reactive<MemberProfileUpdate>({
  title: null, position: null, department: null, organization: null,
  phone: null, addr_house_no: null, addr_moo: null, addr_road: null,
  addr_tambon: null, addr_amphur: null, addr_province: null,
})

// sync form ← profileStore เมื่อโหลดเสร็จ
watch(() => profileStore.profile, (p) => {
  if (!p) return
  Object.assign(form, {
    title: p.title, position: p.position,
    department: p.department, organization: p.organization,
    phone: p.phone, addr_house_no: p.addr_house_no,
    addr_moo: p.addr_moo, addr_road: p.addr_road,
    addr_tambon: p.addr_tambon, addr_amphur: p.addr_amphur,
    addr_province: p.addr_province,
  })
}, { immediate: true })

onMounted(() => profileStore.fetch())
</script>

<template>
  <AppLayout>
    <div class="p-6 max-w-3xl mx-auto">
      <div class="mb-6">
        <h1 class="text-2xl font-bold">ข้อมูลส่วนตัว</h1>
        <p class="text-base-content/60 text-sm mt-1">แก้ไขข้อมูลที่ใช้กรอกแบบฟอร์ม</p>
      </div>

      <div v-if="profileStore.loading" class="flex justify-center py-16">
        <span class="loading loading-spinner loading-lg"></span>
      </div>

      <template v-else>
        <div class="flex flex-col gap-4">
          <ProfileAccountCard />
          <ProfileEditCard
            v-model="form"
            :saving="profileStore.saving"
            :saved="profileStore.saved"
            :error-msg="profileStore.error"
            @save="profileStore.update({ ...form })"
          />
        </div>
      </template>
    </div>
  </AppLayout>
</template>
