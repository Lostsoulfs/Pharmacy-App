#!/usr/bin/env python3
"""Config regression — per-dataset verification flags (ADR-C05).

Covers config.DATA_VERIFIED, the is_unverified() banner predicate, and
the verified_on() date helper. Headless: no tkinter, no DB.

Run under pytest:   pytest tests/test_config.py -q
Run standalone:     python tests/test_config.py
"""

import os
import re
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pharmacy_app.config import (  # noqa: E402
    DATA_VERIFIED, is_unverified, verified_on)

EXPECTED_KEYS = {
    "brand_generic", "red_flags", "lasa_pairs", "sig_abbreviations",
    "common_rx_flags", "vaccines", "law", "tpr",
}
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def test_data_verified_structure():
    assert set(DATA_VERIFIED) == EXPECTED_KEYS
    for value in DATA_VERIFIED.values():
        # Each value is False (unverified) or an ISO verification date.
        assert value is False or (
            isinstance(value, str) and _ISO_DATE.match(value))


def test_unverified_when_any_domain_unverified(monkeypatch):
    monkeypatch.setitem(DATA_VERIFIED, "brand_generic", "2026-05-20")
    monkeypatch.setitem(DATA_VERIFIED, "red_flags", False)
    assert is_unverified(["red_flags", "brand_generic"]) is True


def test_verified_when_all_domains_verified(monkeypatch):
    monkeypatch.setitem(DATA_VERIFIED, "brand_generic", "2026-05-20")
    monkeypatch.setitem(DATA_VERIFIED, "common_rx_flags", "2026-05-20")
    assert is_unverified(["brand_generic", "common_rx_flags"]) is False


def test_unknown_key_fails_safe():
    assert is_unverified(["not_a_real_dataset"]) is True


def test_empty_domains_fails_safe():
    assert is_unverified([]) is True
    assert is_unverified(None) is True


def test_verified_on_returns_latest_date(monkeypatch):
    monkeypatch.setitem(DATA_VERIFIED, "law", "2026-05-20")
    monkeypatch.setitem(DATA_VERIFIED, "tpr", "2026-06-01")
    assert verified_on(["law", "tpr"]) == "2026-06-01"


def test_verified_on_none_when_any_unverified(monkeypatch):
    monkeypatch.setitem(DATA_VERIFIED, "law", False)
    assert verified_on(["law", "tpr"]) is None


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
