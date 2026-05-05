# 00 — System Design Philosophy

---

## 🏛️ ปรัชญาการออกแบบสถาปัตยกรรม (Architecture Philosophy)

เพื่อความยั่งยืน ความปลอดภัย และความง่ายในการบำรุงรักษาระบบ **CoopForm** เรายึดถือหลักการ 3 ประการดังนี้:

### 1. การแบ่งเป็น Layer ที่มีหน้าที่เฉพาะ (Strict Layering)
ระบบถูกออกแบบให้แยกหน้าที่กันอย่างเด็ดขาด (Separation of Concerns) เพื่อลดความซับซ้อน:
- **API Layer (Router):** รับ/ส่งข้อมูลผ่าน Protocol (HTTP/REST) และจัดการเรื่อง Authentication เท่านั้น
- **Service Layer (Business Logic):** เป็นหัวใจของระบบ จัดการเรื่องกฎเกณฑ์การกู้เงิน (Validation) และกระบวนการทำงาน (Workflow)
- **Engine Layer (Internal Tools):** งานเฉพาะทางที่ซับซ้อน เช่น PDF Engine สำหรับวาดเอกสาร หรือ Notification Engine สำหรับส่งข้อความ
- **Data Access Layer (Repository/Models):** จัดการการคุยกับ Database และความถูกต้องของ Schema

### 2. การสื่อสารด้วย Custom Protocol ระหว่าง Layer (Contract-Driven)
แต่ละ Layer จะไม่คุยกันด้วย "ดิบ" (Raw Data) แต่จะคุยกันผ่าน "สัญญา" ที่ตกลงกันไว้:
- ใช้ **Pydantic Schemas (Backend)** และ **TypeScript Interfaces/Zod (Frontend)** เป็น Protocol หลัก
- ข้อมูลจาก Database จะถูกแปลงเป็น Schema ก่อนส่งออกเสมอ เพื่อป้องกันไม่ให้ความลับของ DB รั่วไหล (Data Leaking)
- การสื่อสารภายใน Layer จะต้องชัดเจน มีการส่งผ่านข้อมูลที่ผ่านการ Validate แล้วเท่านั้น

### 3. Loose Coupling (ความไม่ผูกติดกัน)
แต่ละส่วนประกอบต้องสามารถทำงานได้โดยพึ่งพาผู้อื่นให้น้อยที่สุด:
- **Interchangeable:** เราต้องสามารถเปลี่ยน Library หรือเครื่องมือใน Engine Layer ได้ (เช่น เปลี่ยน PDF library) โดยไม่กระทบ Service หรือ API
- **Independent Testing:** แต่ละ Layer ต้องสามารถเขียน Test แยกกันได้
- **Framework Agnostic:** Business Logic สำคัญต้องไม่ผูกติดกับ FastAPI หรือ Vue มากเกินไป เพื่อให้ง่ายต่อการย้ายหรืออัปเกรดในอนาคต

### 4. Data Integrity & Legal Snapshot (ความถูกต้องทางกฎหมาย)
เนื่องจากระบบเกี่ยวข้องกับสัญญาเงินกู้ ข้อมูลต้องมีความถูกต้องแม่นยำและตรวจสอบได้:
- **Snapshot Pattern:** เมื่อมีการยืนยันข้อมูลหรือลงนาม ข้อมูลที่เกี่ยวข้อง (เช่น ชื่อ, ตำแหน่ง, ที่อยู่) ต้องถูก "ทำสำเนา" ลงในตารางสัญญาโดยตรง ไม่ใช่แค่การเชื่อมโยง (Link) ไปยัง Profile เพื่อให้ข้อมูลในสัญญายังคงเดิมแม้เวลาจะผ่านไป
- **Immutability:** ข้อมูลที่ผ่านการอนุมัติแล้วจะไม่มีการแก้ไข (Delete/Update) แต่จะใช้วิธีการสร้าง Version ใหม่หรือการ Cancel แทน

### 5. Auditability & Traceability (การตรวจสอบย้อนกลับ)
ทุกการกระทำที่มีผลต่อสถานะของคำขอต้องมีร่องรอยเสมอ:
- **Audit Logs:** บันทึก Who, When, What และ Why (เหตุผลการอนุมัติ/ปฏิเสธ) ในทุกขั้นตอนสำคัญ
- **Digital Footprint:** บันทึกข้อมูลประกอบ เช่น IP Address และ Metadata ของระบบในขณะที่มีการลงนาม

### 6. Simplicity over Over-Engineering (เน้นความเรียบง่าย)
เลือกใช้วิธีการที่ซับซ้อนน้อยที่สุดที่ยังสามารถแก้ปัญหาได้ (Keep It Simple, Stupid):
- **YAGNI (You Ain't Gonna Need It):** ไม่เพิ่มระบบที่ซับซ้อน (เช่น Redis, Message Queue, Microservices) หากโหลดของระบบยังไม่ถึงจุดที่จำเป็น เพื่อให้การดูแลรักษา (Maintenance) ทำได้ง่ายและประหยัดงบประมาณ
- **Monolith First:** เริ่มต้นด้วยโครงสร้างที่จัดการง่ายในก้อนเดียว แต่แยก Layer ให้ดีเพื่อให้แยกส่วนได้ง่ายในอนาคต

### 7. Agile & Iterative Development (ก้าวหน้าอย่างต่อเนื่อง)
เราเชื่อในการส่งมอบคุณค่าทีละน้อยแต่สม่ำเสมอ แทนการทำโปรเจกต์ขนาดใหญ่ในครั้งเดียว:
- **Small Sprints:** แบ่งงานเป็นหน่วยย่อย (Sprints) ที่สามารถส่งมอบ "ซอฟต์แวร์ที่ใช้งานได้จริง" ในทุกรอบการทำงาน
- **Continuous Feedback:** ดึง Project Owner เข้ามามีส่วนร่วมในทุกการตัดสินใจและทุก Demo เพื่อให้มั่นใจว่าเรากำลังสร้างสิ่งที่ "ใช่" สำหรับผู้ใช้จริงๆ
- **Responding to Change:** พร้อมที่จะ Refactor หรือปรับปรุงส่วนสำคัญของระบบ (แม้จะเป็นส่วน Core) หากพบข้อมูลหรือความต้องการใหม่ที่ดีกว่าเดิม (เช่น การปรับ ER-Diagram กลางคันเพื่อคุณภาพที่ดีขึ้น)

### 8. Sprint Retrospective (การเรียนรู้จากอดีต)
ในทุกการสิ้นสุดรอบการทำงาน (Sprint) เราต้องมีการบันทึกสรุปเพื่อการพัฒนาทีมอย่างต่อเนื่อง:
- **Lessons Learned:** สิ่งที่ได้เรียนรู้ใหม่ๆ จากการพัฒนา
- **Technics:** เทคนิคการเขียนโค้ดหรือการใช้เครื่องมือที่พบว่ามีประสิทธิภาพ
- **Mistakes:** ข้อผิดพลาดที่เกิดขึ้นจริงเพื่อให้ทีมอื่นหรือตัวเองไม่ทำซ้ำ
- **Cautions:** ข้อควรระวังหรือความเสี่ยงที่อาจเกิดขึ้นในอนาคต

### 9. The Cockpit Principle (หน้าปัดเครื่องบิน)
เรายึดหลักการออกแบบ "ห้องนักบิน" เพื่อให้ผู้ดูแลระบบมีอำนาจการตัดสินใจบนพื้นฐานของข้อมูลที่ครบถ้วน (Data-Driven Decision):
- **Total Visibility (Know Everything):** มาตรวัด (Gauges) ต้องแสดงสถานะความจริงที่เป็นปัจจุบันเสมอ (Real-time Truth) ไม่ว่าจะเป็นสุขภาพของฐานข้อมูล (Database Health), ปริมาณการใช้พื้นที่เก็บไฟล์ (Storage Consumption), หรือสถานะของระบบเครือข่าย เพื่อให้ตรวจพบความผิดปกติได้ก่อนจะเกิดวิกฤต
- **Total Control (Control Everything):** แผงสวิตช์ (Switches) ต้องรวมศูนย์ (Centralized Control) เพื่อให้สามารถสับสวิตช์ปรับเปลี่ยนกฎเกณฑ์ของระบบ (Business Rules) ได้ทันทีโดยไม่ต้อง Build หรือ Deploy โค้ดใหม่ (เช่น การเปิด-ปิดระบบตรวจสอบข้อมูล หรือโหมดซ่อมบำรุง)
- **Fail-Safe & Auditability:** ทุกการขยับสวิตช์บนหน้าปัดต้องมีการบันทึกร่องรอย (Logged) และมีระบบป้องกันการกดผิด (Safety Covers) เพื่อให้มั่นใจว่าการควบคุมนั้นเป็นไปอย่างตั้งใจและโปร่งใส
- **Transparency over Obscurity:** ความซับซ้อนของระบบเบื้องหลังต้องถูกแปลงเป็นข้อมูลที่เข้าใจง่ายบนหน้าปัด เพื่อให้การตัดสินใจในสภาวะวิกฤตทำได้อย่างแม่นยำและรวดเร็ว

### 10. Form Modularization — Config Isolated, Engine Shared

ระบบรองรับแบบฟอร์มจำนวนมาก (เป็นร้อยประเภท) โดยยึดหลัก **"config แยก, engine ร่วม"**:

- **Config ต่อ form type** — แต่ละฟอร์มมี TOML config ของตัวเอง กำหนด steps, validation rules, และ PDF field mappings โดยไม่กระทบฟอร์มอื่น
- **Form Engine ร่วมกัน** — `FormEngine` class อ่าน config → render Generic Wizard → fill PDF ผ่าน engine เดียว
- **Component sharing** — shared step components (Step1PersonalInfo, StepAttachments, StepSignatureHub) ใช้ร่วมกันได้ทุกฟอร์ม; form-specific components isolate อยู่ใน folder ของตัวเอง
- **Gate rule:** ห้าม hardcode Wizard หรือ `_map_*()` function สำหรับฟอร์มที่ 3 ขึ้นไป — ต้องผ่าน Form Engine เสมอ

> เพิ่มฟอร์มใหม่ = เพิ่ม TOML + component เดียว ไม่แตะ engine core

### 12. Testing Philosophy — Integration Over Isolation

> *"A test that passes on mocks but fails in production has negative value — it gives false confidence."*

ระบบที่เกี่ยวข้องกับสัญญาเงินกู้และ PDF generation ต้องการ integration test เป็นหลัก ไม่ใช่ unit test ที่ mock ทุกอย่าง:

- **ไม่ mock Database** — ทุก test ที่เกี่ยวกับ data ต้องใช้ SQLite in-memory จริง เหตุผล: Sprint 12 พิสูจน์ว่า 19 bugs ทั้งหมดซ่อนอยู่ใน integration layer — mock จะ pass ทั้งหมด
- **Fresh DB ต่อ test** — แต่ละ test case ได้ DB สะอาด ป้องกัน state contamination ระหว่าง tests
- **Mock ได้เฉพาะ external services** — LINE Notify, Email, Virus scanner — สิ่งที่ไม่มีใน dev environment จริง
- **Unit test เหมาะกับ Pure Functions** — `baht_to_text()`, Zod schemas, validation logic ที่ไม่มี side effect
- **ลำดับความสำคัญ:** Integration tests (DB + API) > Unit tests (pure logic) > E2E tests (UAT)

---

### 11. Component Communication Architecture (SE Perspective)

> *"A component that knows too much about its environment is a component that cannot be moved."*

ระบบ Form ที่ดีทำงานเหมือนวงจรไฟฟ้า — กระแสไหลทิศทางเดียว ทุก node รู้หน้าที่ตัวเอง และไม่มี node ไหนที่ต้องรู้จักทุกอย่างในระบบ

#### 11.1 ลำดับชั้นการสื่อสาร (Communication Hierarchy)

```
┌─────────────────────────────────────────────────────┐
│  Level 1: Component ↔ Component                     │
│           props (ลงล่าง) + events/emit (ขึ้นบน)    │
│           Pattern: v-model (modelValue + update:)   │
├─────────────────────────────────────────────────────┤
│  Level 2: Component ↔ Application State             │
│           Pinia Store (reactive, centralized)       │
│           เฉพาะ Wizard/Page layer เท่านั้น          │
├─────────────────────────────────────────────────────┤
│  Level 3: Application State ↔ Backend               │
│           Service Layer (draftService, authService) │
│           Store เรียก Service — ไม่มีทางลัด        │
├─────────────────────────────────────────────────────┤
│  ❌ FORBIDDEN: Component → API โดยตรง               │
│     Component ต้อง emit event ขึ้นไปให้ Store/Page  │
└─────────────────────────────────────────────────────┘
```

#### 11.2 Pure vs Smart Component — เลือกอย่างมีสติ

**Pure Component** (props in → events out):
```vue
<!-- ✅ ทดสอบง่าย ใช้ซ้ำได้ทุกที่ ไม่ผูกกับ store -->
<Step1PersonalInfo :model-value="form.step1" @update:model-value="form.updateStep1" />
```
- ใช้กับ: Input steps, Form fields, Primitive UI elements
- เกณฑ์: Component นี้อาจถูกใช้ใน context อื่น (เช่น modal, inline edit) หรือไม่?
- ถ้าใช่ → ต้องเป็น Pure

**Smart Component** (อ่าน Store โดยตรง):
```vue
<!-- ✅ ยอมรับได้ เมื่อ component ต้องรวมข้อมูลจากหลาย steps -->
<!-- Step4SignatureHub อ่าน form.step3.guarantors เพื่อแสดงชื่อผู้ค้ำ -->
```
- ใช้กับ: Orchestration steps ที่ต้องการข้อมูลจากหลาย sources
- เกณฑ์: Component นี้จะ*ไม่มีวัน*ถูกนำไปใช้นอก wizard นี้หรือไม่?
- ถ้าใช่ → Smart Component ยอมรับได้ แต่ต้องบันทึกไว้

**กฎเหล็ก:** Smart Component อ่าน Store ได้ แต่ต้องไม่เรียก API โดยตรง

#### 11.3 The Service Layer Contract — เส้นที่ต้องไม่ข้าม

```
❌ Component เรียก api.post('/attachments/...') โดยตรง
✅ Component emit('upload', file) → Store เรียก attachmentService.upload(file)
```

เหตุผล:
1. **Error handling** — Store กำหนด error state กลาง Component ไม่ต้องจัดการ network error
2. **Loading state** — Store บอก UI ว่า "กำลังโหลด" ได้ทุก component พร้อมกัน
3. **Retry logic** — ใส่ใน service layer ครั้งเดียว ใช้ได้ทุกที่
4. **Testability** — Mock service ใน unit test แทนที่จะ mock axios

#### 11.4 The Snapshot Principle ในบริบท Frontend

เมื่อผู้ใช้กดปุ่ม "ยืนยัน/ลงนาม" ข้อมูลต้องถูก freeze ณ จุดนั้น:

```typescript
// ❌ เก็บแค่ reference — ข้อมูลเปลี่ยนได้ในภายหลัง
signature.borrower_id = form.step1.member_code

// ✅ Snapshot — ข้อมูลตรึงอยู่กับลายเซ็นตลอดกาล
signature.snapshot = {
  name: `${form.step1.title}${form.step1.first_name} ${form.step1.last_name}`,
  position: form.step1.position,
  department: form.step1.department,
  signed_at: new Date().toISOString()
}
```

สำคัญเพราะ: สัญญาเงินกู้เป็นเอกสารทางกฎหมาย ถ้าผู้กู้เปลี่ยนชื่อภายหลัง ข้อมูลในสัญญาต้องยังเป็นชื่อ ณ วันทำสัญญา

#### 11.5 Anti-Patterns ที่พบบ่อยใน Form Systems

| Anti-Pattern | อาการ | วิธีแก้ |
|---|---|---|
| **God Component** | Component เดียวทำทุกอย่าง — กรอก, validate, save, navigate | แยก responsibility ออกเป็น child components |
| **Prop Drilling** | ส่ง prop ผ่าน 4-5 ชั้นเพื่อให้ถึง grandchild | ใช้ Pinia store หรือ provide/inject |
| **Direct API Call** | Component เรียก `axios.post()` โดยตรง | ย้ายไป Service layer, component emit event |
| **Mutable Props** | Child แก้ไข prop โดยตรง (`props.data.name = ...`) | ใช้ emit + v-model pattern เสมอ |
| **Store Bloat** | Store เก็บ UI state (modal open/close, hover) | UI state อยู่ใน component local ref เท่านั้น |

#### 11.6 Backend Service Layer Anti-Patterns

| Anti-Pattern | อาการ | วิธีแก้ |
|---|---|---|
| **Fat Router** | Router มี business logic (คำนวณดอกเบี้ย, validate workflow) โดยตรง | ย้าย logic ทั้งหมดไป Service layer, router เหลือแค่ auth + schema validation |
| **Naked ORM Query** | Router หรือ Service เรียก `session.query(Model).filter(...)` กระจัดกระจาย | รวม query ไว้ใน Service method เดียว — ง่ายต่อการ test และ audit |
| **Implicit Lazy Load** | Access `app.generated_pdf` หลัง async session ปิดแล้ว → `MissingGreenlet` | ใช้ `selectinload()` หรือ `joinedload()` ใน query เสมอเมื่อ relationship ถูกใช้ |
| **Raw Dict as User** | ใช้ `current_user["id"]` บางที่ + `current_user.id` อีกที่ | กำหนด `CurrentUser` TypedDict หรือ Pydantic model ครั้งเดียว ใช้ทั้ง codebase |
| **Hardcoded Path** | `"data/attachments/..."` ในโค้ด | ใช้ `settings.DATA_DIR` จาก config เสมอ — deploy ที่ไหนก็ได้ |
| **Unauthenticated Admin Route** | `/system/stats`, `/backup` เปิดโล่ง | ทุก route ต้องมี `Depends(require_role("staff"))` อย่างน้อย — ไม่มีข้อยกเว้น |

---

### 13. Documentation Drives Code — เอกสารนำทางโค้ดเสมอ

> *"Code without documentation is a decision without reasoning. Future developers — including yourself — deserve to know the why, not just the what."*

**กฎเหล็กของ CoopForm:** เอกสารต้องเสร็จก่อน โค้ดจึงเริ่มได้

#### ลำดับที่ต้องทำทุก Sprint ทุกครั้ง ไม่มีข้อยกเว้น

```
1. เขียน Sprint Doc (*.md ใน doc/bible_claude_version/sprint_XX/)
   └─ เป้าหมาย, scope, definition of done, design decisions
        ↓
2. breakdown เป็น Tasks (TodoWrite)
        ↓
3. เขียนโค้ด (อ้างอิง Sprint Doc ตลอด)
        ↓
4. อัปเดต Roadmap (11_roadmap.md)
```

#### ทำไมต้องทำก่อนโค้ด

| ถ้าไม่มีเอกสาร | ผลที่เกิด |
|---|---|
| ไม่รู้ว่า scope จบที่ไหน | โค้ดขยายเกินกำหนด (scope creep) |
| ไม่บันทึก design decision | Sprint ถัดไปตัดสินใจซ้ำ (ซึ่งอาจผิดพลาดเหมือนเดิม) |
| ไม่มี definition of done | ไม่รู้ว่า "เสร็จ" หมายความว่าอะไร |
| ไม่มี context ใน doc | Claude ต้อง read codebase ใหม่ทุกครั้ง (เสียเวลา) |

#### เอกสาร = Memory ของโปรเจกต์

- **Sprint Doc** — บันทึก what + why + decisions ของแต่ละ sprint
- **Philosophy (ไฟล์นี้)** — หลักการที่ไม่เปลี่ยนแปลง กำกับทุกการตัดสินใจ
- **Roadmap** — ภาพรวม progress และ backlog ที่เป็น single source of truth
- **ADR (Architecture Decision Records)** — บันทึกการตัดสินใจสำคัญที่ส่งผลระยะยาว

#### กฎปฏิบัติ

- ถ้า Claude เสนอว่าจะ "เริ่มโค้ดเลย" — ให้หยุดและถามว่า "Sprint Doc เสร็จหรือยัง?"
- ถ้า feature ไม่มีใน Sprint Doc — ไม่ implement จนกว่าจะ document ก่อน
- Design decision ที่เกิดระหว่าง coding ต้องบันทึกย้อนหลังใน Sprint Doc ทันที

---

> *"Architecture is the decisions that you wish you could get right early in a project."*  
> ด้วยหลักการเหล่านี้ เรากำลังตัดสินใจเพื่ออนาคตของ CoopForm — ระบบที่สามารถขยาย บำรุงรักษา และส่งต่อได้โดยไม่ต้องอธิบาย
