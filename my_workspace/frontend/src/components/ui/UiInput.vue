<script setup lang="ts">
defineProps<{
  label: string
  modelValue: string | null | undefined
  type?: string
  placeholder?: string
  required?: boolean
  size?: 'sm' | 'md'
  error?: string
}>()

const emit = defineEmits<{ 'update:modelValue': [string] }>()
</script>

<template>
  <div>
    <label class="label text-sm">
      {{ label }}<span v-if="required" class="text-error ml-0.5">*</span>
    </label>
    <input
      :value="modelValue ?? ''"
      :type="type ?? 'text'"
      :placeholder="placeholder"
      class="input input-bordered w-full"
      :class="[size === 'sm' ? 'input-sm' : '', error ? 'input-error' : '']"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <p v-if="error" class="text-error text-xs mt-1">{{ error }}</p>
  </div>
</template>
