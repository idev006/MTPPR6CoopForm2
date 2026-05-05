# Sprint 9 Retrospective: Supporting Documents & The Cockpit

**Period:** 2026-04-26 to 2026-04-27
**Goal:** Implement PDF Uploads, Validation Engine, and Centralized Control (Cockpit).

---

## 🎓 1. Lessons Learned (บทเรียนที่ได้รับ)
- **Centralized Control is King:** การแยกกฎการตรวจสอบ (Validation Rules) ออกมาจาก Business Logic และควบคุมผ่าน Config กลาง ช่วยให้ระบบมีความยืดหยุ่นสูงมาก (Agility) สามารถปรับเปลี่ยนพฤติกรรมแอปได้โดยไม่ต้อง Deploy โค้ดใหม่
- **Single Source of Truth (SSOT):** การแชร์ค่าคอนฟิกจาก Backend ไปยัง Frontend ผ่าน API ช่วยลดความซ้ำซ้อนและป้องกันความผิดพลาดที่เกิดจากความไม่สอดคล้องกันของข้อมูล (Data Desync)
- **Visual Aid UX:** การใช้ภาพอ้างอิงจริง (หน้าปัด Checklist) ช่วยลดอัตราการส่งเอกสารผิดพลาดได้อย่างมีนัยสำคัญ

## 💡 2. Technics (เทคนิคต่างๆ)
- **Chain of Responsibility Pattern:** ใช้ใน `validators.py` เพื่อทำระบบ Validation Pipeline ที่สามารถเพิ่ม/ลดกฎการตรวจสอบได้ง่ายเหมือนต่อจิ๊กซอว์
- **Dynamic Path Discovery:** เทคนิคการค้นหา Path ของไฟล์คอนฟิกแบบสัมพัทธ์กับตำแหน่งโค้ด ทำให้ระบบรันได้ทุกที่ทั้งบน Windows, Linux และ Docker
- **Interactive Checklist UI:** การสร้างความสัมพันธ์ระหว่างไฟล์ที่อัปโหลดกับรายการ Checklist ในฝั่ง Frontend เพื่อให้ Feedback กับผู้ใช้แบบ Real-time

## ❌ 3. Mistakes (ข้อผิดพลาดที่เกิดขึ้น)
- **Missing Dependencies:** ลืมติดตั้ง `python-multipart` ทำให้ระบบอัปโหลดพังในช่วงแรก (แก้โดยการอัปเดต requirements.txt)
- **Import Ordering:** เกิด `NameError` และ `ImportError` จากการประกาศฟังก์ชันและตัวแปรผิดลำดับ (Circular Dependency)
- **Vite Compilation:** ลืมนำ Macro `defineProps` ออกจากการ Import ใน Vue 3 ทำให้เกิด Runtime Error

## ⚠️ 4. Cautions (ข้อควรระวัง)
- **ForeignKey Constraints:** การผูกเอกสารแนบ (Attachment) กับใบสมัคร (LoanApplication) โดยตรงอาจมีปัญหาในขั้นตอนการบันทึกร่าง (Draft) เพราะใบสมัครจริงยังไม่ถูกสร้าง ควรใช้ UUID ที่เชื่อมโยงกันแทน
- **Master Switch Warning:** หากปิด Master Switch ใน Production จะเป็นความเสี่ยงด้านความปลอดภัยสูง ควรมีระบบแจ้งเตือน (Alert) เมื่อสวิตช์สำคัญถูกปิด
- **File System Persistence:** บน Docker ต้องมั่นใจว่ามีการทำ Volume Mount สำหรับโฟลเดอร์เอกสารแนบ มิฉะนั้นไฟล์จะหายเมื่อ Restart Container

---

## 📊 Sprint Statistics
- **Total Files Created/Updated:** 12 files
- **Key Feature:** Supporting Document Wizard, System Cockpit, Validation Engine
- **Status:** COMPLETED ✅
