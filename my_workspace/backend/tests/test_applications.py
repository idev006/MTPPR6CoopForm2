"""
test_applications.py — Regression tests for Sprint 12 H-01/H-02 and Sprint 15 UUID fix
Coverage: submit ordinary/emergency, list, detail+ownership, cancel guard
"""
from httpx import AsyncClient

from app.models.user import User

# Minimal form data — backend accepts Dict[str, Any], no strict validation
_ORDINARY_PAYLOAD = {
    "step1": {
        "title": "ด.ต.", "first_name": "สมชาย", "last_name": "ใจดี",
        "id_card": "3101234567891", "member_code": "T001",
        "position": "ผู้บังคับหมู่", "department": "กก.สส.ภ.จว.เชียงใหม่",
        "salary": 25000, "marital_status": "single",
        "current_addr": {"house_no": "1", "tambon": "t", "amphur": "a", "province": "p"},
        "register_addr": {"house_no": "1", "tambon": "t", "amphur": "a", "province": "p"},
    },
    "step2": {
        "loan_amount": 100000, "repayment_period": 24,
        "loan_purpose": "ซื้อที่ดิน", "payout_method": "cash",
    },
    "step3": {"guarantors": []},
    "step4": {"borrower_sig": {"signed": True, "signature_base64": "data:image/png;base64,abc"}},
    "step5": {"checklist": []},
    "step6": {"contract_no": "001/2568"},
}

_EMERGENCY_PAYLOAD = {
    "step1": {
        "title": "ด.ต.", "first_name": "วีระ", "last_name": "สุขใจ",
        "id_card": "3109876543210", "member_code": "T002",
        "position": "ผู้บังคับหมู่", "department": "กก.",
        "salary": 20000, "marital_status": "single",
        "current_addr": {"house_no": "2", "tambon": "t", "amphur": "a", "province": "p"},
        "register_addr": {"house_no": "2", "tambon": "t", "amphur": "a", "province": "p"},
    },
    "step2": {
        "loan_amount": 10000, "repayment_period": 6,
        "loan_purpose": "ค่ารักษาพยาบาล", "payout_method": "cash",
    },
    "step4": {"borrower_sig": {"signed": True, "signature_base64": "data:image/png;base64,abc"}},
}


async def test_submit_ordinary_loan(client: AsyncClient, borrower_user: User, borrower_token: str):
    resp = await client.post(
        "/api/v1/applications",
        json=_ORDINARY_PAYLOAD,
        headers={"Authorization": f"Bearer {borrower_token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["application_no"].startswith("ORD-")
    # Regression: application_id must be a string, not UUID object (Sprint 15 bug fix)
    assert isinstance(body["application_id"], str)


async def test_submit_emergency_loan(client: AsyncClient, borrower_user: User, borrower_token: str):
    resp = await client.post(
        "/api/v1/applications/emergency",
        json=_EMERGENCY_PAYLOAD,
        headers={"Authorization": f"Bearer {borrower_token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["application_no"].startswith("EMG-")


async def test_get_my_applications(client: AsyncClient, borrower_user: User, borrower_token: str):
    # Submit one application first
    await client.post(
        "/api/v1/applications",
        json=_ORDINARY_PAYLOAD,
        headers={"Authorization": f"Bearer {borrower_token}"},
    )
    resp = await client.get(
        "/api/v1/applications/me",
        headers={"Authorization": f"Bearer {borrower_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    assert body[0]["form_type"] == "ordinary"


async def test_get_application_detail_ownership(
    client: AsyncClient,
    borrower_user: User,
    borrower_token: str,
    staff_user: User,
    staff_token: str,
):
    # Borrower submits
    submit_resp = await client.post(
        "/api/v1/applications",
        json=_ORDINARY_PAYLOAD,
        headers={"Authorization": f"Bearer {borrower_token}"},
    )
    app_id = submit_resp.json()["application_id"]

    # Owner can access
    detail_resp = await client.get(
        f"/api/v1/applications/{app_id}",
        headers={"Authorization": f"Bearer {borrower_token}"},
    )
    assert detail_resp.status_code == 200

    # Staff (different user, not the applicant) gets 403
    forbidden_resp = await client.get(
        f"/api/v1/applications/{app_id}",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert forbidden_resp.status_code == 403


async def test_cancel_non_submitted_is_rejected(
    client: AsyncClient,
    borrower_user: User,
    borrower_token: str,
):
    # Submit an application (status = "submitted")
    submit_resp = await client.post(
        "/api/v1/applications",
        json=_ORDINARY_PAYLOAD,
        headers={"Authorization": f"Bearer {borrower_token}"},
    )
    app_id = submit_resp.json()["application_id"]

    # Cancel it (should succeed)
    cancel_resp = await client.post(
        f"/api/v1/applications/{app_id}/cancel",
        headers={"Authorization": f"Bearer {borrower_token}"},
    )
    assert cancel_resp.status_code == 200

    # Try to cancel again (status = "cancelled" now → must get 400)
    cancel_again_resp = await client.post(
        f"/api/v1/applications/{app_id}/cancel",
        headers={"Authorization": f"Bearer {borrower_token}"},
    )
    assert cancel_again_resp.status_code == 400
