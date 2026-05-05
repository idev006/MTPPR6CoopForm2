"""
test_thai_baht.py — Unit tests for baht_to_text() (Sprint 14 utility)
Pure function: no DB, no fixtures needed.
"""
import pytest

from app.utils.thai_baht import baht_to_text


@pytest.mark.parametrize("amount, expected", [
    (0,           "ศูนย์บาทถ้วน"),
    (1,           "หนึ่งบาทถ้วน"),
    (11,          "สิบเอ็ดบาทถ้วน"),
    (20,          "ยี่สิบบาทถ้วน"),
    (21,          "ยี่สิบเอ็ดบาทถ้วน"),
    (100,         "หนึ่งร้อยบาทถ้วน"),
    (1000,        "หนึ่งพันบาทถ้วน"),
    (500000,      "ห้าแสนบาทถ้วน"),
    (1000000,     "หนึ่งล้านบาทถ้วน"),
    (500000.50,   "ห้าแสนบาทห้าสิบสตางค์"),
    (1.25,        "หนึ่งบาทยี่สิบห้าสตางค์"),
])
def test_baht_to_text(amount, expected):
    assert baht_to_text(amount) == expected


def test_negative_raises():
    with pytest.raises(ValueError):
        baht_to_text(-1)
