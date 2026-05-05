# Sprint 4.5 — Dev Environment Setup + Tailwind v4 / DaisyUI v5 Migration

**วันที่:** 2026-04-26  
**สถานะ:** ✅ COMPLETE

---

## สิ่งที่ทำในสปรินท์นี้

### 1. Dev Environment Setup

| ขั้นตอน | รายละเอียด |
|---|---|
| Virtual env | `F:\programming\python\MTPPR6CoopForm2\Scripts\activate` |
| Backend packages | `pip install -r requirements.txt` — bcrypt downgrade 5.0→4.3.0 |
| Frontend packages | `npm install` — 251 packages |
| Seed DB | `python seed_dev.py` — skip (users มีอยู่แล้วจาก Sprint 4) |
| Backend server | `uvicorn app.main:app --reload` → http://localhost:8000 |
| Frontend server | `npm run dev` → http://localhost:5173 |

### 2. DaisyUI v4 → v5.5.19 Upgrade

```bash
npm i -D daisyui@latest
```

DaisyUI v5 ต้องการ Tailwind CSS v4 — จึงต้องอัปเกรด Tailwind ด้วย

### 3. Tailwind CSS v3 → v4.2.4 Migration

```bash
npm install -D tailwindcss@latest @tailwindcss/vite
```

**การเปลี่ยนแปลงสำคัญ v3→v4:**

| เดิม (v3) | ใหม่ (v4) |
|---|---|
| `postcss.config.js` + tailwindcss plugin | `@tailwindcss/vite` Vite plugin (ลบ postcss.config.js) |
| `tailwind.config.js` | ลบออก — ย้าย config เข้า CSS |
| `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| `plugins: [require('daisyui')]` | `@plugin "daisyui"` ใน CSS |
| `theme.extend.fontFamily` ใน JS | `@theme { --font-sans: ... }` ใน CSS |
| `content: [...]` ใน JS | `@source "..."` ใน CSS |

### 4. ไฟล์ที่เปลี่ยน

**`src/assets/main.css` (ใหม่):**
```css
@import "tailwindcss";
@plugin "daisyui";

@theme {
  --font-sans: 'Sarabun', sans-serif;
}

@source "../index.html";
@source "./**/*.{vue,js,ts,jsx,tsx}";
```

**`vite.config.ts` (เพิ่ม):**
```ts
import tailwindcss from '@tailwindcss/vite'
// plugins: [vue(), tailwindcss()]
```

**`package.json` (เพิ่ม):**
```json
"type": "module"
```

**ไฟล์ที่ลบออก:**
- `tailwind.config.js`
- `postcss.config.js`

---

## ปัญหาที่เจอและวิธีแก้

### ปัญหา 1: `@layer base` + no `@tailwind base`
**สาเหตุ:** `tailwind.config.js` ยังอยู่ → Tailwind v4 switch ไปใช้ PostCSS path แทน Vite plugin path  
**แก้:** ลบ `tailwind.config.js` ออก

### ปัญหา 2: ESM-only error (`@tailwindcss/vite`)
**สาเหตุ:** `package.json` ไม่มี `"type": "module"`  
**แก้:** เพิ่ม `"type": "module"` ใน `package.json`

### ปัญหา 3: DaisyUI theme ไม่ load (หน้าขาวโพลน)
**สาเหตุ:** `@plugin "daisyui" { themes: light; }` syntax ผิดใน v5  
**แก้:** ใช้ `@plugin "daisyui";` เรียบๆ (ไม่มี config block)

---

## สถานะปัจจุบัน

- Backend: ✅ `http://localhost:8000/api/health` → `{"status":"ok"}`
- Frontend: ✅ `http://localhost:5173/login` — DaisyUI v5 theme แสดงผลถูกต้อง
- Auth: ✅ `borrower@coop.local / Test1234!` → Dashboard, `staff@coop.local / Test1234!` → /staff

---

## Sprint ถัดไป: Sprint 5 — Phase 3 Form Wizard

**เป้าหมาย:** Multi-step Form กรอกได้ + Auto-save + member profile endpoints

**งานที่ต้องทำ (เรียงลำดับ):**
1. Backend: `member_service.py` + `GET/PUT /members/me/profile`
2. Backend: `draft_service.py` + draft endpoints
3. Frontend: `ProfilePage.vue`
4. Frontend: `FormWizard.vue` + Step 1–3
5. Frontend: `useAutoSave.ts`
