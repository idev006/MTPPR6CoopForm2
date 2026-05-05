<script setup lang="ts">
import { computed, ref } from 'vue'
import { useFormStore } from '@/stores/form.store'
import UiSignaturePad from '@/components/ui/UiSignaturePad.vue'
import type { SignatureData } from '@/types/form'

const form = useFormStore()

// State for which person is currently signing
const signingActor = ref<{ id: string; label: string; title: string } | null>(null)
const superiorName = ref(form.step4.superior_sig.signer_name ?? '')
const superiorPosition = ref(form.step4.superior_sig.signer_position ?? '')

function startSigning(id: string, label: string, title: string) {
  signingActor.value = { id, label, title }
}

function handleSaveSignature(base64: string) {
  if (!signingActor.value) return

  const sig: SignatureData = {
    signed: true,
    signed_at: new Date().toISOString(),
    signature_base64: base64
  }

  const id = signingActor.value.id
  if (id === 'borrower') {
    form.step4.borrower_sig = sig
  } else if (id === 'spouse') {
    form.step4.spouse_sig = sig
  } else if (id === 'superior') {
    form.step4.superior_sig = { ...sig, signer_name: superiorName.value, signer_position: superiorPosition.value }
  } else if (id.startsWith('guarantor_')) {
    const idx = parseInt(id.split('_')[1])
    const isSpouse = id.includes('_spouse_')
    if (isSpouse) {
      const gIdx = parseInt(id.split('_spouse_')[1])
      while (form.step4.guarantor_spouse_sigs.length <= gIdx) form.step4.guarantor_spouse_sigs.push({ signed: false })
      form.step4.guarantor_spouse_sigs[gIdx] = sig
    } else {
      while (form.step4.guarantor_sigs.length <= idx) form.step4.guarantor_sigs.push({ signed: false })
      form.step4.guarantor_sigs[idx] = sig
    }
  }

  form.markDirty()
  signingActor.value = null
}

const guarantorList = computed(() => form.step3.guarantors)
</script>

<template>
  <div class="space-y-6">
    <header class="text-center mb-8">
      <h2 class="text-2xl font-bold text-base-content">ศูนย์รวมลายเซ็น</h2>
      <p class="text-base-content/60">กรุณานำแท็บเล็ตไปให้ผู้เกี่ยวข้องลงนามให้ครบถ้วน</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- 1. Borrower -->
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body p-4">
          <div class="flex justify-between items-start">
            <div>
              <span class="badge badge-primary badge-sm mb-1">ผู้ขอกู้</span>
              <h3 class="font-bold text-lg">{{ form.step1.title }}{{ form.step1.first_name }} {{ form.step1.last_name }}</h3>
              <p class="text-xs text-base-content/50">เจ้าของคำขอ</p>
            </div>
            <div v-if="form.step4.borrower_sig.signed" class="text-success text-sm font-bold flex items-center gap-1">
              <span class="text-lg">✓</span> เซ็นแล้ว
            </div>
          </div>
          
          <div class="mt-4 flex justify-center bg-white rounded-lg border border-base-300 h-24 overflow-hidden relative group">
            <img v-if="form.step4.borrower_sig.signature_base64" :src="form.step4.borrower_sig.signature_base64" class="h-full object-contain" />
            <div v-else class="flex items-center justify-center text-base-content/20 italic text-sm">ยังไม่ได้ลงนาม</div>
            <button 
              class="absolute inset-0 bg-primary/80 text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center font-bold"
              @click="startSigning('borrower', 'ผู้ขอกู้', 'ลงลายมือชื่อผู้ขอกู้')"
            >
              {{ form.step4.borrower_sig.signed ? 'เซ็นใหม่' : 'กดเพื่อเซ็นชื่อ' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 2. Spouse (Conditional based on Marital Status) -->
      <div v-if="form.step1.marital_status === 'married'" class="card bg-base-200/50 border border-base-300">
        <div class="card-body p-4">
          <div class="flex justify-between items-start">
            <div>
              <span class="badge badge-secondary badge-sm mb-1">คู่สมรส</span>
              <h3 class="font-bold text-lg">{{ form.step1.spouse_name || 'คู่สมรส' }}</h3>
              <p class="text-xs text-base-content/50">คำยินยอมให้ทำนิติกรรม</p>
            </div>
            <div v-if="form.step4.spouse_sig.signed" class="text-success text-sm font-bold flex items-center gap-1">
              <span class="text-lg">✓</span> เซ็นแล้ว
            </div>
          </div>
          
          <div class="mt-4 flex justify-center bg-white rounded-lg border border-base-300 h-24 overflow-hidden relative group">
            <img v-if="form.step4.spouse_sig.signature_base64" :src="form.step4.spouse_sig.signature_base64" class="h-full object-contain" />
            <div v-else class="flex items-center justify-center text-base-content/20 italic text-sm">ยังไม่ได้ลงนาม</div>
            <button 
              class="absolute inset-0 bg-primary/80 text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center font-bold"
              @click="startSigning('spouse', 'คู่สมรส', `ลงลายมือชื่อคู่สมรส (${form.step1.spouse_name || ''})`)"
            >
              {{ form.step4.spouse_sig.signed ? 'เซ็นใหม่' : 'กดเพื่อเซ็นชื่อ' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 3. Guarantors (Loop) -->
      <template v-for="(g, idx) in guarantorList" :key="idx">
        <div class="card bg-base-200/50 border border-base-300">
          <div class="card-body p-4">
            <div class="flex justify-between items-start">
              <div>
                <span class="badge badge-accent badge-sm mb-1">ผู้ค้ำประกันคนที่ {{ idx + 1 }}</span>
                <h3 class="font-bold text-lg">{{ g.name }}</h3>
                <p class="text-xs text-base-content/50">{{ g.position }}</p>
              </div>
              <div v-if="form.step4.guarantor_sigs[idx]?.signed" class="text-success text-sm font-bold flex items-center gap-1">
                <span class="text-lg">✓</span> เซ็นแล้ว
              </div>
            </div>
            
            <div class="mt-4 flex justify-center bg-white rounded-lg border border-base-300 h-24 overflow-hidden relative group">
              <img v-if="form.step4.guarantor_sigs[idx]?.signature_base64" :src="form.step4.guarantor_sigs[idx]?.signature_base64" class="h-full object-contain" />
              <div v-else class="flex items-center justify-center text-base-content/20 italic text-sm">ยังไม่ได้ลงนาม</div>
              <button 
                class="absolute inset-0 bg-primary/80 text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center font-bold"
                @click="startSigning(`guarantor_${idx}`, `ผู้ค้ำคนที่ ${idx + 1}`, `ลงลายมือชื่อผู้ค้ำประกัน (${g.name})`)"
              >
                {{ form.step4.guarantor_sigs[idx]?.signed ? 'เซ็นใหม่' : 'กดเพื่อเซ็นชื่อ' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Guarantor's Spouse (Conditional) -->
        <div v-if="g.marital_status === 'married'" class="card bg-base-200/50 border border-base-300">
          <div class="card-body p-4">
            <div class="flex justify-between items-start">
              <div>
                <span class="badge badge-outline badge-sm mb-1">คู่สมรสผู้ค้ำคนที่ {{ idx + 1 }}</span>
                <h3 class="font-bold text-lg">{{ g.spouse_name || 'คู่สมรสผู้ค้ำ' }}</h3>
                <p class="text-xs text-base-content/50">คำยินยอมผู้ค้ำประกัน</p>
              </div>
              <div v-if="form.step4.guarantor_spouse_sigs[idx]?.signed" class="text-success text-sm font-bold flex items-center gap-1">
                <span class="text-lg">✓</span> เซ็นแล้ว
              </div>
            </div>
            
            <div class="mt-4 flex justify-center bg-white rounded-lg border border-base-300 h-24 overflow-hidden relative group">
              <img v-if="form.step4.guarantor_spouse_sigs[idx]?.signature_base64" :src="form.step4.guarantor_spouse_sigs[idx]?.signature_base64" class="h-full object-contain" />
              <div v-else class="flex items-center justify-center text-base-content/20 italic text-sm">ยังไม่ได้ลงนาม</div>
              <button 
                class="absolute inset-0 bg-primary/80 text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center font-bold"
                @click="startSigning(`guarantor_spouse_${idx}`, `คู่สมรสผู้ค้ำคนที่ ${idx + 1}`, `ยินยอมค้ำประกัน (${g.spouse_name || ''})`)"
              >
                {{ form.step4.guarantor_spouse_sigs[idx]?.signed ? 'เซ็นใหม่' : 'กดเพื่อเซ็นชื่อ' }}
              </button>
            </div>
          </div>
        </div>
      </template>

      <!-- 4. Superior -->
      <div class="card bg-base-200/50 border border-base-300">
        <div class="card-body p-4">
          <div class="flex justify-between items-start">
            <div>
              <span class="badge badge-neutral badge-sm mb-1">ผู้บังคับบัญชา</span>
              <h3 class="font-bold text-lg">ความเห็นผู้บังคับบัญชา</h3>
              <p class="text-xs text-base-content/50">พิจารณาให้ความเห็นและลงนาม</p>
            </div>
            <div v-if="form.step4.superior_sig.signed" class="text-success text-sm font-bold flex items-center gap-1">
              <span class="text-lg">✓</span> เซ็นแล้ว
            </div>
          </div>

          <div class="mt-2 flex gap-4 text-sm font-medium">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" v-model="form.step4.superior_opinion" value="true" class="radio radio-primary radio-sm" />
              เห็นควรสนับสนุน
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" v-model="form.step4.superior_opinion" value="false" class="radio radio-error radio-sm" />
              ไม่เห็นควรสนับสนุน
            </label>
          </div>

          <div class="mt-3 grid grid-cols-2 gap-2">
            <div>
              <label class="label py-0.5 text-xs font-bold">ชื่อ-นามสกุล</label>
              <input
                v-model="superiorName"
                @change="form.step4.superior_sig = { ...form.step4.superior_sig, signer_name: superiorName }; form.markDirty()"
                type="text" placeholder="เช่น พ.ต.อ. สุรชัย ใจดี"
                class="input input-bordered input-sm w-full"
              />
            </div>
            <div>
              <label class="label py-0.5 text-xs font-bold">ตำแหน่ง</label>
              <input
                v-model="superiorPosition"
                @change="form.step4.superior_sig = { ...form.step4.superior_sig, signer_position: superiorPosition }; form.markDirty()"
                type="text" placeholder="เช่น ผกก."
                class="input input-bordered input-sm w-full"
              />
            </div>
          </div>

          <div class="mt-3 flex justify-center bg-white rounded-lg border border-base-300 h-24 overflow-hidden relative group">
            <img v-if="form.step4.superior_sig.signature_base64" :src="form.step4.superior_sig.signature_base64" class="h-full object-contain" />
            <div v-else class="flex items-center justify-center text-base-content/20 italic text-sm">ยังไม่ได้ลงนาม</div>
            <button
              class="absolute inset-0 bg-primary/80 text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center font-bold"
              @click="startSigning('superior', 'ผู้บังคับบัญชา', 'ลงลายมือชื่อผู้บังคับบัญชา')"
            >
              {{ form.step4.superior_sig.signed ? 'เซ็นใหม่' : 'กดเพื่อเซ็นชื่อ' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Signature Pad Modal -->
    <UiSignaturePad 
      v-if="signingActor"
      :title="signingActor.title"
      :placeholder="`กรุณาให้ ${signingActor.label} เซ็นภายในกรอบนี้`"
      @save="handleSaveSignature"
      @cancel="signingActor = null"
    />
  </div>
</template>
