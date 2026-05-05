<script setup lang="ts">
import { useUiStore, THEMES, type Theme } from '@/stores/ui.store'

// dropdownClass ควบคุมทิศทาง: 'dropdown-end' (default) | 'dropdown-top' | 'dropdown-right'
const props = withDefaults(defineProps<{ dropdownClass?: string }>(), {
  dropdownClass: 'dropdown-end',
})

const ui = useUiStore()
</script>

<template>
  <div :class="['dropdown', props.dropdownClass]">
    <div tabindex="0" role="button" class="btn btn-ghost btn-sm gap-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
      </svg>
      <span class="hidden sm:inline text-xs">{{ ui.theme }}</span>
    </div>

    <div tabindex="0" class="dropdown-content bg-base-100 rounded-box shadow-2xl z-50 mt-1 w-52 max-h-80 overflow-y-auto p-1 border border-base-300">
      <div
        v-for="t in THEMES"
        :key="t"
        :data-theme="t"
        class="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer hover:bg-base-200 transition-colors border-l-2 border-l-transparent"
        :class="{ 'bg-base-300 !border-l-primary': ui.theme === t }"
        @click="ui.setTheme(t as Theme)"
      >
        <!-- Color swatches from that theme -->
        <div class="flex gap-0.5 shrink-0">
          <div class="w-2 h-5 rounded-sm bg-primary"></div>
          <div class="w-2 h-5 rounded-sm bg-secondary"></div>
          <div class="w-2 h-5 rounded-sm bg-accent"></div>
          <div class="w-2 h-5 rounded-sm bg-neutral"></div>
        </div>
        <span class="text-base-content text-sm capitalize flex-1">{{ t }}</span>
        <svg v-if="ui.theme === t" xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-primary shrink-0" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>
  </div>
</template>
