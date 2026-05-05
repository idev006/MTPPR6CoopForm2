<script setup lang="ts">
defineProps<{
  title: string
  description: string
  actionLabel: string
  actionDisabled?: boolean
  variant?: 'primary' | 'ghost'
}>()

const emit = defineEmits<{ action: [] }>()
</script>

<template>
  <div class="card bg-base-100 shadow-sm">
    <div class="card-body">
      <h2 class="card-title text-lg">{{ title }}</h2>
      <p class="text-sm text-base-content/60">{{ description }}</p>
      <div class="card-actions mt-2">
        <button
          class="btn btn-sm"
          :class="variant === 'ghost' ? 'btn-ghost' : 'btn-primary'"
          :disabled="actionDisabled"
          @click="emit('action')"
        >
          {{ actionLabel }}
        </button>
      </div>
    </div>
  </div>
</template>
