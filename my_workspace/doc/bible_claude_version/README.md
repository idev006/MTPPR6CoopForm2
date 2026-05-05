# CoopForm System — Project Bible

**Version:** 1.0  
**วันที่:** 26 เมษายน 2568  
**ผู้จัดทำ:** Claude Sonnet 4.6 (จาก Brainstorm Session กับ Project Owner)  
**Project:** MTPPR6CoopForm2

---

## สารบัญ

| ไฟล์ | เนื้อหา |
|------|---------|
| [00_design_philosophy.md](00_design_philosophy.md) | **Core Philosophy**, Layers, Protocols, Coupling |
| [01_vision.md](01_vision.md) | Vision, Goals, Objectives, Problem Statement |
| [02_requirements.md](02_requirements.md) | Functional & Non-Functional Requirements |
| [03_actors_usecases.md](03_actors_usecases.md) | Actors, Use Cases, Use Case Diagrams |
| [04_architecture.md](04_architecture.md) | System Architecture, Component Diagrams, C4 Model |
| [05_database.md](05_database.md) | Database Design, ERD, Schema |
| [06_api_design.md](06_api_design.md) | REST API Endpoints, Request/Response |
| [07_frontend.md](07_frontend.md) | Frontend Architecture, MVVM, Component Tree |
| [08_pdf_engine.md](08_pdf_engine.md) | PDF Engine Design (pikepdf + reportlab, Sprint Findings) |
| [09_security.md](09_security.md) | Security Design, RBAC, JWT |
| [10_deployment.md](10_deployment.md) | Docker, Directory Structure, Persistence Strategy |
| [11_roadmap.md](11_roadmap.md) | Development Phases, Sprint Planning |
| [12_decisions.md](12_decisions.md) | Architecture Decision Records (ADR) |

---

## 🏃 Sprint Logs (History)

| Sprint | Description | Files |
|--------|-------------|-------|
| **Sprint 4 & 5** | Dev Env, Form Wizard (Tabs 1-3) | [Documents](sprint_04_05/) |
| **Sprint 6** | 7-Tab Wizard, Signature Hub, 100% PDF Compliance | [Documents](sprint_06/) |
| **Sprint 7** | PDF Engine, Validation, Submission Workflow | [Documents](sprint_07/) |
| **Sprint 8** | Staff Workflow & Application Review | [Documents](sprint_08/) |
| **Sprint 9** | Supporting Docs, Validation Engine, Cockpit, Production Hardening | [Documents](sprint_09/) |
| **Sprint 10** | Architecture Decoupling (src/forms/), Toast, Auto-draft fix, Notification bug fix | [Documents](sprint_10/) |

---

## ข้อมูลสำคัญของโปรเจกต์ (Quick Reference)

```
ระบบ      : CoopForm — ระบบกรอกแบบฟอร์มขอกู้เงินสหกรณ์ออนไลน์
Scale     : ~200 สมาชิก / ~30 req/hr (peak)
Roles     : borrower (ผู้ขอกู้) | staff (เจ้าหน้าที่สหกรณ์)
PDF       : AcroForm Fillable PDF (Adobe Acrobat Pro DC)
Library   : pikepdf + reportlab (พิสูจน์แล้วใน Sprint 1-2)
Stack     : FastAPI + PostgreSQL + Vue 3 + DaisyUI
Deploy    : Docker (nginx + api + db) — 3 containers
```

---

## Design Principles ที่ตกลงกัน

1. **API First** — Frontend และ Backend แยกจากกันสมบูรณ์
2. **Loose Coupling UI** — Form Step components แยกต่อ form type, share เฉพาะ UI primitive
3. **Simplicity over Flexibility** — ตัด Redis, Celery, MinIO ออก (scale ไม่ถึง)
4. **Proven PDF Stack** — ใช้ pikepdf + reportlab เท่านั้น (ไม่ใช้ pypdf.update_page_form_field_values)
5. **Data Persistence First** — ออกแบบ Docker volumes และ directory structure ก่อน code
