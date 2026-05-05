<template>
  <!-- DaisyUI menu item: li > RouterLink, class="active" คือ DaisyUI active state -->
  <li>
    <RouterLink
      :to="resolvedPath"
      :class="{ 'active': isActive }"
      @click="closeDrawer"
    >
      <span class="text-base leading-none">{{ item.icon }}</span>
      <span class="flex-1">{{ item.label }}</span>
      <span
        v-if="badge && badge > 0"
        class="badge badge-sm badge-error"
      >
        {{ badge > 99 ? '99+' : badge }}
      </span>
    </RouterLink>
  </li>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type { NavItem } from '@/configs/navigation'

const props = defineProps<{
  item: NavItem
  badge?: number
}>()

const route = useRoute()

// แปลง path ที่มี ?status= query string ให้เป็น RouterLink to object
const resolvedPath = computed(() => {
  if (props.item.path.includes('?status=')) {
    const [path, status] = props.item.path.split('?status=')
    return { path, query: { status } }
  }
  return props.item.path
})

const isActive = computed(() => {
  if (props.item.exact) {
    return route.path === props.item.path && !route.query.status
  }
  if (props.item.path.includes('?status=')) {
    const [basePath, status] = props.item.path.split('?status=')
    return route.path === basePath && route.query.status === status
  }
  return route.path.startsWith(props.item.path)
})

// ปิด DaisyUI drawer เมื่อคลิก nav item (บน mobile/tablet)
function closeDrawer() {
  const el = document.getElementById('app-drawer') as HTMLInputElement | null
  if (el) el.checked = false
}
</script>
