#!/usr/bin/env python3
"""Config regression — per-dataset verification flags (ADR-C05).

Covers config.DATA_VERIFIED and the is_unverified() banner predicate.
Headless: no tkinter, no DB.

Run under pytest:   pytest tests/test_config.py -q
Run standalone:     python tests/test_config.py
"""

import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pharmacy_app.config import DATA_VERIFIED, is_unverified  # noqa: E402

EXPECTED_KEYS = {
    "brand_generic", "red_flags", "lasa_pairs", "sig_abbreviations",
    "common_rx_flags", "vaccines", "law", "tpr",
}


def test_data_verified_structure():
    assert set(DATA_VERIFIED) == EXPECTED_KEYS
    assert all(isinstance(v, bool) for v in DATA_VERIFIED.values())


def test_unverified_when_any_domain_unverified(monkeypatch):
    monkeypatch.setitem(DATA_VERIFIED, "brand_generic", True)
    monkeypatch.setitem(DATA_VERIFIED, "red_flags", False)
    assert is_unverified(["red_flags", "brand_generic"]) is True


def test_verified_when_all_domains_verified(monkeypatch):
    monkeypatch.setitem(DATA_VERIFIED, "brand_generic", True)
    monkeypatch.setitem(DATA_VERIFIED, "common_rx_flags", True)
    assert is_unverified(["brand_generic", "common_rx_flags"]) is False


def test_unknown_key_fails_safe():
    assert is_unverified(["not_a_real_dataset"]) is True


def test_empty_domains_fails_safe():
    assert is_unverified([]) is True
    assert is_unverified(None) is True


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
