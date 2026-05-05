<script setup lang="ts">
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import { useAuth } from '@/composables/useAuth'

const schema = toTypedSchema(
  z.object({
    email: z.string().min(1, 'กรุณากรอกอีเมล').email('รูปแบบอีเมลไม่ถูกต้อง'),
    password: z.string().min(1, 'กรุณากรอกรหัสผ่าน'),
  }),
)

const { handleSubmit, defineField, errors } = useForm({ validationSchema: schema })
const [email, emailAttrs] = defineField('email')
const [password, passwordAttrs] = defineField('password')

const { login, loading, error } = useAuth()

const onSubmit = handleSubmit(async (values) => {
  await login(values.email, values.password)
})
</script>

<template>
  <div class="card w-full max-w-sm shadow-xl bg-base-100">
    <div class="card-body">
      <h2 class="card-title justify-center text-2xl">เข้าสู่ระบบ</h2>
      <p class="text-center text-sm text-base-content/60 mb-2">ระบบกรอกแบบฟอร์มขอกู้เงินสหกรณ์</p>

      <div v-if="error" role="alert" class="alert alert-error text-sm py-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M12 3a9 9 0 110 18A9 9 0 0112 3z" />
        </svg>
        <span>{{ error }}</span>
      </div>

      <form @submit="onSubmit" class="flex flex-col gap-3 mt-2" novalidate>
        <div class="form-control">
          <label class="label pb-1">
            <span class="label-text font-medium">อีเมล</span>
          </label>
          <input
            v-model="email" v-bind="emailAttrs"
            type="email" placeholder="example@email.com" autocomplete="email"
            class="input input-bordered" :class="{ 'input-error': errors.email }"
          />
          <label v-if="errors.email" class="label pt-1">
            <span class="label-text-alt text-error">{{ errors.email }}</span>
          </label>
        </div>

        <div class="form-control">
          <label class="label pb-1">
            <span class="label-text font-medium">รหัสผ่าน</span>
          </label>
          <input
            v-model="password" v-bind="passwordAttrs"
            type="password" placeholder="••••••••" autocomplete="current-password"
            class="input input-bordered" :class="{ 'input-error': errors.password }"
          />
          <label v-if="errors.password" class="label pt-1">
            <span class="label-text-alt text-error">{{ errors.password }}</span>
          </label>
        </div>

        <button type="submit" class="btn btn-primary mt-2" :disabled="loading">
          <span v-if="loading" class="loading loading-spinner loading-sm" />
          {{ loading ? 'กำลังเข้าสู่ระบบ...' : 'เข้าสู่ระบบ' }}
        </button>
      </form>
    </div>
  </div>
</template>
