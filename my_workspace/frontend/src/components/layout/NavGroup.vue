<template>
  <!-- DaisyUI menu group: li > details > summary + ul -->
  <li>
    <details :open="open" @toggle="open = ($event.target as HTMLDetailsElement).open">
      <summary class="font-medium">
        <span class="text-base leading-none">{{ group.icon }}</span>
        {{ group.label }}
      </summary>
      <ul>
        <NavItem
          v-for="child in group.children"
          :key="child.path"
          :item="child"
        />
      </ul>
    </details>
  </li>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { NavGroup } from '@/configs/navigation'
import NavItem from './NavItem.vue'

const props = defineProps<{ group: NavGroup }>()
const open = ref(props.group.defaultOpen ?? false)
</script>
