<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useUiStore } from '@/stores/ui.store'
import { useSystemStore } from '@/stores/system.store'
import { onMounted } from 'vue'

const ui = useUiStore()
const system = useSystemStore()

ui.initTheme()

onMounted(() => {
  system.fetchConfig()
})
</script>

<template>
  <RouterView />
</template>
