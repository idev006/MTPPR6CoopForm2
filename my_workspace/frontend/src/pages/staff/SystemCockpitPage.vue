<script setup lang="ts">
import { onMounted } from 'vue'
import { useSystemStore } from '@/stores/system.store'

const system = useSystemStore()

onMounted(() => {
  system.fetchConfig()
  system.fetchStats()
})

const refresh = () => {
  system.fetchStats()
}
</script>

<template>
  <div class="min-h-screen bg-base-200 p-4 md:p-8">
    <div class="max-w-6xl mx-auto space-y-8">
      <!-- Header -->
      <header class="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 class="text-3xl font-black tracking-tight text-primary flex items-center gap-3">
            <span class="text-4xl">🕹️</span> SYSTEM COCKPIT
          </h1>
          <p class="text-base-content/50 text-sm uppercase tracking-widest font-bold">Command & Control Center</p>
        </div>
        <div class="flex items-center gap-2">
          <div class="badge badge-success gap-2 py-3 px-4 font-bold text-white shadow-sm">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
            </span>
            SYSTEM: {{ system.stats.system.status }}
          </div>
          <button @click="refresh" class="btn btn-circle btn-ghost" :class="{ 'animate-spin': !system.loaded }">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
          </button>
        </div>
      </header>

      <!-- The Gauges (Stats) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Database Gauge -->
        <div class="card bg-white shadow-xl border-l-4 border-primary">
          <div class="card-body p-6">
            <h3 class="card-title text-base-content/40 text-xs uppercase font-black tracking-widest">Database Health</h3>
            <div class="flex items-end justify-between mt-2">
              <div>
                <p class="text-4xl font-black text-primary">{{ system.stats.database.total_applications }}</p>
                <p class="text-[10px] font-bold text-base-content/40 uppercase">Total Apps</p>
              </div>
              <div class="text-right">
                <p class="text-xl font-bold">{{ system.stats.database.pending_review }}</p>
                <p class="text-[10px] font-bold text-warning uppercase">Pending</p>
              </div>
            </div>
            <div class="w-full bg-base-200 h-2 rounded-full mt-4 overflow-hidden">
               <div class="bg-primary h-full" :style="{ width: '80%' }"></div>
            </div>
          </div>
        </div>

        <!-- Storage Gauge -->
        <div class="card bg-white shadow-xl border-l-4 border-secondary">
          <div class="card-body p-6">
            <h3 class="card-title text-base-content/40 text-xs uppercase font-black tracking-widest">Storage Consumption</h3>
            <div class="flex items-end justify-between mt-2">
              <div>
                <p class="text-4xl font-black text-secondary">{{ system.stats.storage.attachment_total_size_mb }} <span class="text-sm">MB</span></p>
                <p class="text-[10px] font-bold text-base-content/40 uppercase">Filesystem</p>
              </div>
              <div class="text-right">
                <p class="text-xl font-bold">{{ system.stats.storage.attachment_count }}</p>
                <p class="text-[10px] font-bold text-base-content/40 uppercase">Total Files</p>
              </div>
            </div>
            <div class="w-full bg-base-200 h-2 rounded-full mt-4 overflow-hidden">
               <div class="bg-secondary h-full" :style="{ width: '30%' }"></div>
            </div>
          </div>
        </div>

        <!-- System Info -->
        <div class="card bg-neutral text-neutral-content shadow-xl">
          <div class="card-body p-6">
            <h3 class="card-title text-white/40 text-xs uppercase font-black tracking-widest">Infrastructure</h3>
            <div class="space-y-2 mt-4">
              <div class="flex justify-between text-xs font-bold border-b border-white/10 pb-2">
                <span>Environment:</span>
                <span class="text-success uppercase">{{ system.stats.system.environment }}</span>
              </div>
              <div class="flex justify-between text-xs font-bold border-b border-white/10 pb-2">
                <span>Node Version:</span>
                <span>Production 1.2.0</span>
              </div>
              <div class="flex justify-between text-xs font-bold">
                <span>Uptime:</span>
                <span class="text-info">99.9%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- The Switches (Control Panel) -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div class="space-y-6">
          <h2 class="text-xl font-black flex items-center gap-2">
            <span class="w-2 h-6 bg-primary rounded-full"></span>
            MASTER SWITCHES
          </h2>
          
          <div class="card bg-white shadow-xl overflow-hidden">
            <div class="p-6 space-y-6">
              <!-- Global Toggle -->
              <div class="flex items-center justify-between p-4 bg-primary/5 rounded-2xl border border-primary/20">
                <div>
                  <h4 class="font-black text-primary">GLOBAL VALIDATION ENGINE</h4>
                  <p class="text-xs text-primary/60">ควบคุมการตรวจสอบข้อมูลทั้งหมดของระบบ</p>
                </div>
                <input type="checkbox" class="toggle toggle-primary toggle-lg" :checked="system.config.validation.enabled" disabled />
              </div>

              <!-- Specific Toggles -->
              <div class="space-y-4">
                 <div class="flex items-center justify-between px-2">
                   <div class="flex items-center gap-3">
                     <div class="w-10 h-10 rounded-xl bg-base-200 flex items-center justify-center">📏</div>
                     <div>
                       <p class="font-bold text-sm">File Size Validation</p>
                       <p class="text-[10px] opacity-50 uppercase">Limit: {{ system.config.storage.max_size_mb }}MB</p>
                     </div>
                   </div>
                   <input type="checkbox" class="toggle toggle-sm" :checked="system.config.validation.check_file_size" disabled />
                 </div>

                 <div class="flex items-center justify-between px-2">
                   <div class="flex items-center gap-3">
                     <div class="w-10 h-10 rounded-xl bg-base-200 flex items-center justify-center">📄</div>
                     <div>
                       <p class="font-bold text-sm">MIME Type Validation</p>
                       <p class="text-[10px] opacity-50 uppercase">PDF Only Mode</p>
                     </div>
                   </div>
                   <input type="checkbox" class="toggle toggle-sm" :checked="system.config.validation.check_file_type" disabled />
                 </div>
              </div>

              <div class="alert alert-warning text-xs font-bold py-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-4 w-4" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                <span>สวิตช์ควบคุมเหล่านี้ถูกตั้งค่าผ่าน app.toml บนเครื่อง Server เพื่อความปลอดภัยสูงสุด</span>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <h2 class="text-xl font-black flex items-center gap-2">
            <span class="w-2 h-6 bg-secondary rounded-full"></span>
            SYSTEM ACTIONS
          </h2>
          <div class="grid grid-cols-2 gap-4">
             <button 
               @click="system.clearCache"
               class="btn btn-neutral h-32 flex flex-col gap-2 rounded-3xl border-2 border-base-300 group hover:border-primary transition-all duration-300"
             >
               <span class="text-3xl group-hover:scale-125 transition-transform">🧹</span>
               <div class="text-center">
                 <p class="font-bold text-xs">Clear PDF Cache</p>
                 <p class="text-[9px] opacity-50">Delete all generated files</p>
               </div>
             </button>
             <button 
               @click="system.triggerBackup"
               class="btn btn-neutral h-32 flex flex-col gap-2 rounded-3xl border-2 border-base-300 group hover:border-secondary transition-all duration-300"
             >
               <span class="text-3xl group-hover:scale-125 transition-transform">📥</span>
               <div class="text-center">
                 <p class="font-bold text-xs">Backup Database</p>
                 <p class="text-[9px] opacity-50">Generate .sql dump</p>
               </div>
             </button>
             <button class="btn btn-error h-32 flex flex-col gap-2 rounded-3xl text-white shadow-lg group hover:brightness-110 transition-all">
               <span class="text-3xl group-hover:animate-pulse">🛑</span>
               <div class="text-center">
                 <p class="font-bold text-xs">Maintenance Mode</p>
                 <p class="text-[9px] text-white/50">Stop all new applications</p>
               </div>
             </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
