import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { memberService } from '@/services/member.service'
import type { MemberProfile, MemberProfileUpdate } from '@/types/member'
import type { Step1Data } from '@/types/form'

export const useProfileStore = defineStore('profile', () => {
  const profile = ref<MemberProfile | null>(null)
  const loading = ref(false)
  const saving  = ref(false)
  const saved   = ref(false)
  const error   = ref('')

  // ── ดึงข้อมูล (cache — ถ้าโหลดแล้วไม่โหลดซ้ำ) ──────
  async function fetch(force = false) {
    if (profile.value && !force) return
    loading.value = true
    error.value = ''
    try {
      profile.value = await memberService.getProfile()
    } catch {
      error.value = 'โหลดข้อมูลไม่สำเร็จ'
    } finally {
      loading.value = false
    }
  }

  async function update(data: MemberProfileUpdate) {
    saving.value = true
    saved.value  = false
    error.value  = ''
    try {
      profile.value = await memberService.updateProfile(data)
      saved.value   = true
      setTimeout(() => { saved.value = false }, 3000)
    } catch {
      error.value = 'บันทึกไม่สำเร็จ กรุณาลองใหม่'
    } finally {
      saving.value = false
    }
  }

  // ── ดึงข้อมูล profile มา pre-fill Step1 ────────────
  const step1Prefill = computed<Partial<Step1Data>>(() => {
    if (!profile.value) return {}
    const p = profile.value
    return {
      title:        p.title        ?? '',
      first_name:   p.first_name   ?? '',
      last_name:    p.last_name    ?? '',
      member_code:  p.member_code  ?? '',
      id_card:      p.national_id  ?? '',
      position:     p.position     ?? '',
      department:   p.department   ?? '',
      organization: p.organization ?? '',
      phone:        p.phone        ?? '',
      salary:       p.salary       ?? null,
      shares_amount: p.shares_amount ?? null,
      existing_debt: p.existing_debt ?? null,
      // profile เก็บที่อยู่เดียว → ใช้เป็น current_addr (ที่อยู่ปัจจุบัน)
      current_addr: {
        house_no: p.addr_house_no ?? '',
        moo:      p.addr_moo      ?? '',
        road:     p.addr_road     ?? '',
        tambon:   p.addr_tambon   ?? '',
        amphur:   p.addr_amphur   ?? '',
        province: p.addr_province ?? '',
      },
    }
  })

  function reset() {
    profile.value = null
    error.value   = ''
  }

  return { profile, loading, saving, saved, error, step1Prefill, fetch, update, reset }
})
