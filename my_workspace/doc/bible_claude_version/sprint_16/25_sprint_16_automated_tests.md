# Sprint 16 — Automated Tests

**วันที่:** 2026-04-29  
**เป้าหมาย:** สร้าง automated test suite ครอบคลุม regression จาก Sprint 12 (19 bugs) และ Sprint 14-15

---

## Milestone Overview

```
M1 — Backend Infrastructure   pytest.ini + conftest.py upgrade
M2 — test_auth.py              5 test cases (login/me/refresh)
M3 — test_applications.py     5 test cases (submit/list/detail/cancel)
M4 — test_thai_baht.py         12 unit cases (baht_to_text pure function)
M5 — Frontend validation.test  8 Zod test cases + vitest.config.ts
M6 — Run & Fix                 1 production bug found + fixed
```

---

## Test Results

### Backend (pytest)
```
22 passed, 21 warnings in 45.42s
```

| ไฟล์ | Cases | ผล |
|---|---|---|
| `test_auth.py` | 5 | ✅ |
| `test_applications.py` | 5 | ✅ |
| `test_thai_baht.py` | 12 | ✅ |

### Frontend (vitest)
```
8 passed in 1.81s
```

| ไฟล์ | Cases | ผล |
|---|---|---|
| `src/schemas/validation.test.ts` | 8 | ✅ |

---

## Files Created / Modified

| File | การเปลี่ยนแปลง |
|---|---|
| `backend/pytest.ini` | `asyncio_mode = auto` |
| `backend/tests/conftest.py` | Full upgrade: test_engine + db_session + client + user/token fixtures |
| `backend/tests/test_auth.py` | 5 cases: login success/fail, get_me, no_token, refresh |
| `backend/tests/test_applications.py` | 5 cases: submit ordinary/emergency, list, detail+ownership, cancel guard |
| `backend/tests/test_thai_baht.py` | 12 parametrized cases + negative test |
| `frontend/vitest.config.ts` | vitest config (node env, `@` alias) |
| `frontend/src/schemas/validation.test.ts` | 8 cases: id_card length, loan_amount min, guarantor min, bank required, emergency max |
| `backend/app/api/v1/routers/applications.py` | Bug fix: `selectinload(generated_pdf)` in GET detail |

---

## Production Bug Found During Testing

**Bug:** `GET /applications/{id}` → `MissingGreenlet` error  
**สาเหตุ:** `app.generated_pdf` เป็น lazy-loaded relationship — async session ไม่รองรับ implicit lazy load  
**แก้ไข:** เพิ่ม `.options(selectinload(LoanApplication.generated_pdf))` ใน query  
**ผลกระทบ:** ถ้าไม่แก้ จะ crash 500 ทุกครั้งที่ดู detail ของ application ที่มี PDF

---

## Test Architecture Decisions

**1. ไม่ Mock Database** — ใช้ SQLite in-memory file (`coopform_test.db`) จริงทุก test  
เหตุผล: Sprint 12 พิสูจน์ว่า mock ซ่อน integration bugs (19 bugs พบจาก real usage ไม่ใช่ unit test)

**2. Fresh session per request (ไม่ใช่ shared session)**  
`conftest.py` — `client` fixture สร้าง `async_sessionmaker` แล้ว yield new session ต่อ request  
เหตุผล: shared session ทำให้ rollback ใน request หนึ่งส่งผลต่อ request ถัดไป (bug พบระหว่าง Sprint 16)

**3. Fixture isolation: `test_engine` scope=function**  
สร้าง tables ก่อนแต่ละ test, drop หลัง — แต่ละ test ได้ DB สะอาด

**4. pytest-asyncio mode=auto**  
ไม่ต้อง `@pytest.mark.asyncio` ทุก function

---

## Regression Coverage Map

| Bug จาก Sprint | Test ที่ครอบคลุม |
|---|---|
| S12 C-01: current_user dict access | `test_submit_ordinary_loan`, `test_get_me` |
| S12 C-04: session restore on reload | `test_refresh_token` |
| S12 H-01/H-02: emergency endpoint | `test_submit_emergency_loan` |
| S12 H-03: Zod schema sync | `validation.test.ts` — id_card, loan_amount, bank_account_no |
| S12 H-04: GuarantorInfo.address | `validation.test.ts` — guarantor min |
| S15: application_id UUID → str | `test_submit_ordinary_loan` (asserts isinstance str) |
| S16 NEW: generated_pdf lazy load | `test_get_application_detail_ownership` |

---

## Run Commands

```bash
# Backend
cd my_workspace/backend
PYTHONUTF8=1 python -m pytest tests/ -v

# Frontend
cd my_workspace/frontend
npx vitest run
```

---

## Definition of Done

- [x] pytest infrastructure: `pytest.ini` + upgraded `conftest.py`
- [x] `test_auth.py`: 5 cases all pass
- [x] `test_applications.py`: 5 cases all pass
- [x] `test_thai_baht.py`: 12 cases all pass
- [x] `validation.test.ts`: 8 cases all pass
- [x] Total: **22 backend + 8 frontend = 30 tests, 30 passed**
- [x] Production bug fixed: `selectinload(generated_pdf)` in detail endpoint

## Status: ✅ DONE (2026-04-29)
