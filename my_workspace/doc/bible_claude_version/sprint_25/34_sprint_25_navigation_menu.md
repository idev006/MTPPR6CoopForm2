# Sprint 25 — Navigation Menu System

**วันที่:** 2026-04-30
**สถานะ:** ✅ DONE (รวม 25.1 Drawer)

---

## เป้าหมาย

เปลี่ยนจาก Top Navbar แบบ flat → **Left Sidebar** (desktop) + **Bottom Navigation** (mobile)
ให้ผู้ใช้รู้ตลอดเวลาว่าอยู่ที่ไหน และไปไหนได้บ้าง — แยก world ระหว่าง Borrower และ Staff อย่างสมบูรณ์

---

## Current State (ก่อน Sprint)

```
AppLayout
  └─ AppNavbar (top bar, horizontal)
       ├─ NAV_ITEMS filter by role (flat list)
       ├─ NotificationBell
       ├─ ThemePicker
       └─ Avatar dropdown (profile + logout)
```

**ปัญหา:**
- Flat menu ไม่รองรับ grouping (เช่น "ยื่นคำขอกู้ > กู้สามัญ / กู้ฉุกเฉิน")
- Staff ไม่เห็น pending count ก่อนคลิก
- Mobile ซ่อนทุกอย่างใน dropdown — UX แย่
- ไม่มี active state ชัดเจนบน mobile

---

## Target State (หลัง Sprint)

```
AppLayout
  └─ div.flex
       ├─ AppSidebar (240px, desktop only)
       │    ├─ Logo + ชื่อระบบ
       │    ├─ NavGroup / NavItem (role-based)
       │    ├─ NotificationBell (footer)
       │    ├─ ThemePicker (footer)
       │    └─ Avatar + Logout (footer)
       └─ main.flex-1
            ├─ MobileTopBar (logo + hamburger, mobile only)
            └─ <slot /> (page content)

BottomNav (mobile, fixed bottom)
  └─ ไอคอน 4-5 จุด: หน้าหลัก / คำขอ / แจ้งเตือน / โปรไฟล์
```

---

## Menu Structure

### Borrower Sidebar

```
┌─────────────────────────┐
│ 🏦 CoopForm             │
│ ───────────────────     │
│ 🏠 หน้าหลัก            │  path: /
│                         │
│ 📝 ยื่นคำขอกู้          │  (collapsible group)
│   ├ กู้สามัญ           │  path: /applications/ordinary/new
│   └ กู้ฉุกเฉิน         │  path: /applications/emergency/new
│                         │
│ 👤 โปรไฟล์              │  path: /profile
│ ─────────────────────── │
│ 🔔 แจ้งเตือน     [3]   │
│ 🎨 ธีม                  │
│ ─────────────────────── │
│ สมชาย รักดี             │
│ [ออกจากระบบ]            │
└─────────────────────────┘
```

### Staff Sidebar

```
┌─────────────────────────┐
│ 🏦 CoopForm — Staff     │
│ ───────────────────     │
│ 🏠 ภาพรวม               │  path: /staff
│                         │
│ 📥 รอดำเนินการ    [5]  │  path: /staff?status=submitted
│ 🔍 กำลังพิจารณา   [2]  │  path: /staff?status=under_review
│ 📎 รอเอกสารเพิ่ม  [1]  │  path: /staff?status=pending_documents
│ ✅ อนุมัติแล้ว          │  path: /staff?status=approved
│ ❌ ปฏิเสธแล้ว           │  path: /staff?status=rejected
│                         │
│ 👥 จัดการสมาชิก         │  path: /staff/members
│ ⚙️  System Cockpit      │  path: /staff/cockpit
│ ─────────────────────── │
│ 🔔 แจ้งเตือน     [8]   │
│ 🎨 ธีม                  │
│ ─────────────────────── │
│ สมหญิง เจ้าหน้าที่      │
│ [ออกจากระบบ]            │
└─────────────────────────┘
```

### Mobile Bottom Navigation

```
Borrower:  [🏠 หน้าหลัก] [📝 คำขอ] [🔔 แจ้งเตือน] [👤 โปรไฟล์]
Staff:     [🏠 ภาพรวม]  [📥 คำขอ] [🔔 แจ้งเตือน] [⚙️ เพิ่มเติม]
```

---

## Definition of Done

- [x] Sidebar แสดงบน desktop (≥ lg breakpoint) ถูกต้องตาม role
- [x] Active state highlight เมื่อ route ตรงกัน
- [x] Staff เห็น badge count (submitted / under_review / pending_documents)
- [x] Badge count poll ทุก 60 วินาที (ใช้ useNavBadges composable)
- [x] Mobile: BottomNav แสดง 4 จุด ถูกต้องตาม role
- [x] Mobile/Tablet: SidebarDrawer (hamburger) ครอบคลุม tablet portrait gap
- [x] ThemePicker + NotificationBell ย้ายไปอยู่ใน Sidebar footer
- [ ] ไม่มี regression บนหน้าอื่น (wizard, review page ยังทำงานได้)

---

## Components ที่จะสร้าง / แก้ไข

| Component | Action | หมายเหตุ |
|---|---|---|
| `src/configs/navigation.ts` | แก้ไข | เพิ่ม NavGroup, icon, badge key |
| `src/composables/useNavBadges.ts` | ใหม่ | ดึง pending count จาก staff API |
| `src/components/layout/AppSidebar.vue` | ใหม่ | Sidebar หลัก |
| `src/components/layout/NavItem.vue` | ใหม่ | item เดี่ยว + active + badge |
| `src/components/layout/NavGroup.vue` | ใหม่ | collapsible group |
| `src/components/layout/BottomNav.vue` | ใหม่ | Mobile fixed bottom |
| `src/components/layout/MobileTopBar.vue` | ใหม่ | Logo bar บน mobile |
| `src/components/AppLayout.vue` | แก้ไข | เพิ่ม sidebar + bottom nav |
| `src/components/AppNavbar.vue` | ลบ / deprecated | แทนที่ด้วย Sidebar |

---

## Navigation Config Schema (ใหม่)

```typescript
export interface NavItem {
  label: string
  path: string
  roles: UserRole[]
  icon: string           // emoji หรือ heroicon name
  exact?: boolean        // ใช้ exact match สำหรับ active state
  badgeKey?: StaffBadgeKey  // key สำหรับดึง count จาก useNavBadges
}

export interface NavGroup {
  label: string
  icon: string
  roles: UserRole[]
  children: NavItem[]
  defaultOpen?: boolean
}

export type NavEntry = NavItem | NavGroup

export type StaffBadgeKey = 'submitted' | 'under_review' | 'pending_documents'
```

---

## useNavBadges Composable

```typescript
// src/composables/useNavBadges.ts
// Staff only — ดึงจำนวนคำขอแต่ละสถานะ
// poll ทุก 60 วินาที (เช่นเดียวกับ NotificationBell)
// return: { submitted, under_review, pending_documents }
```

Backend endpoint ที่ใช้: `GET /staff/applications?status=X`
นับจาก response array length — ไม่ต้องสร้าง endpoint ใหม่

---

## Design Decisions

### D-1: Sidebar ไม่มี collapse (ไม่ใช่ mini sidebar)
เหตุผล: ผู้ใช้ส่วนใหญ่เป็นสมาชิกสหกรณ์ที่ไม่คุ้นเคยกับ webapp
Sidebar แบบเปิดตลอดชัดเจนกว่า — ไม่ต้องเรียนรู้การ hover หรือ toggle

### D-2: Mobile ใช้ BottomNav ไม่ใช่ Hamburger Drawer
Hamburger = ซ่อนทุกอย่าง ผู้ใช้ต้องกดก่อนถึงเห็น
BottomNav = เห็นตลอด 4 จุดหลัก — mobile UX ดีกว่ามาก

### D-3: Badge count ใช้ staff API เดิม
`GET /staff/applications?status=submitted` → `response.length`
ไม่ต้องสร้าง `/staff/stats` endpoint ใหม่
Trade-off: network cost สูงขึ้นเล็กน้อย แต่ไม่ต้องแตะ backend

### D-4: Active state ใช้ `useRoute().path` เทียบกับ `item.path`
ไม่ใช้ `router-link-active` เพราะ `/staff?status=X` จะ active ทั้งหมด
ใช้ full path + query comparison แทน

### D-6: Tablet Portrait Gap → แก้ด้วย DaisyUI Drawer (Option B, Native)

**ปัญหา:** Tablet portrait (768–1023px) ถูก treat เป็น mobile → BottomNav 4 จุด
Staff เข้าไม่ถึง: กำลังพิจารณา / อนุมัติแล้ว / ปฏิเสธแล้ว / จัดการสมาชิก

**แนวทางที่เลือก:** DaisyUI `drawer` layout component (native, ไม่ใช้ Vue state)

**การทำงาน:**
- `AppLayout.vue` ใช้ `<div class="drawer lg:drawer-open">` เป็น root layout
- `lg:drawer-open` = บน desktop sidebar เปิดค้างตลอด
- บน mobile/tablet = drawer ปิดอยู่ ควบคุมด้วย `<input id="app-drawer" type="checkbox" class="drawer-toggle">`
- hamburger บน MobileTopBar เป็น `<label for="app-drawer">` — CSS toggle ล้วน ไม่ต้อง Vue state
- `drawer-overlay` (label) ปิด drawer เมื่อคลิก background
- NavItem.vue ปิด drawer โดย `document.getElementById('app-drawer').checked = false` เมื่อคลิก

**ผลต่อ architecture:**
- ลบ `SidebarDrawer.vue` ทิ้ง (ซ้ำซ้อน)
- ลบ `drawerOpen = ref()` ออกจาก AppLayout
- ลบ `emit('open-drawer')` ออกจาก MobileTopBar
- AppSidebar ถูกใช้ใน `drawer-side` (เดิม: แยกอิสระ)
- NavItem และ NavGroup ใช้ DaisyUI `menu` structure (`<li>`, `<details><summary>`)

### D-7: Navigation ใช้ DaisyUI `menu` + `drawer` Native Components
ไม่เขียน animation, toggle state, overlay เอง — ใช้ DaisyUI component แทนทั้งหมด
- `menu menu-sm` บน `<ul>` wrapper ใน sidebar
- `<li>` เป็น root ของ NavItem/NavGroup
- `class="active"` บน RouterLink = DaisyUI active highlight
- `<details><summary>` ของ DaisyUI = collapsible group (แทน button + v-if)
- badge ใช้ `<span class="badge badge-sm badge-error">` ใน menu item

### D-5: AppNavbar.vue ยังคงอยู่ระหว่าง transition
ไม่ลบทันที — deprecate ก่อน แล้วลบใน Sprint ถัดไป
เพื่อป้องกัน regression ถ้า component อื่นยัง import อยู่

---

## Wireframe — Desktop Layout

```
┌──────────┬─────────────────────────────────────────┐
│ SIDEBAR  │                                         │
│ 240px    │  <slot /> — page content                │
│ fixed    │                                         │
│ left     │  (DashboardPage, ReviewPage, etc.)      │
│          │                                         │
│ [footer] │                                         │
└──────────┴─────────────────────────────────────────┘
```

## Wireframe — Mobile Layout

```
┌─────────────────────────┐
│ [🏦 CoopForm]     [☰]  │  ← MobileTopBar (show logo only, no hamburger needed)
├─────────────────────────┤
│                         │
│  <slot /> — content     │
│                         │
├─────────────────────────┤
│  [🏠]  [📝]  [🔔]  [👤] │  ← BottomNav fixed
└─────────────────────────┘
```
