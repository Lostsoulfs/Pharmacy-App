#!/usr/bin/env python3
"""Tests for pure UI validation helpers.

These tests intentionally avoid tkinter and SQLite so validation behavior can
be locked before panel handlers are wired through it.
"""

import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pharmacy_app.validation import (  # noqa: E402
    MAX_FILTER_LEN,
    MAX_QTY_OWED,
    MAX_SIG_TOKENS,
    validate_filter_text,
    validate_inventory_entry,
    validate_iso_date,
    validate_lookup_query,
    validate_partial_fill,
    validate_positive_int,
    validate_sig_tokens,
    validate_text_field,
)


def test_text_field_trims_and_requires_value():
    assert validate_text_field("  Aspirin  ", "Drug", max_len=20).value == "Aspirin"
    result = validate_text_field("   ", "Drug", max_len=20)
    assert result.ok is False
    assert result.error == "Drug is required."


def test_text_field_caps_length_and_rejects_controls():
    assert validate_text_field("abc", "Field", max_len=2).ok is False
    assert validate_text_field("abc\x00", "Field", max_len=10).ok is False


def test_filter_text_allows_blank_but_caps_length():
    assert validate_filter_text("").ok is True
    assert validate_filter_text("x" * (MAX_FILTER_LEN + 1)).ok is False


def test_iso_date_requires_zero_padded_real_date():
    assert validate_iso_date("2027-03-15").ok is True
    assert validate_iso_date("2027-3-15").ok is False
    assert validate_iso_date("2027-02-29").ok is False


def test_positive_int_accepts_only_bounded_whole_numbers():
    assert validate_positive_int("12", "Qty").value == 12
    assert validate_positive_int("0", "Qty").ok is False
    assert validate_positive_int("-1", "Qty").ok is False
    assert validate_positive_int("1.5", "Qty").ok is False
    assert validate_positive_int(str(MAX_QTY_OWED + 1), "Qty").ok is False


def test_lookup_query_requires_two_characters():
    assert validate_lookup_query("li").ok is True
    assert validate_lookup_query("l").ok is False


def test_sig_tokens_normalize_and_reject_junk():
    result = validate_sig_tokens(" po qd prn ")
    assert result.ok is True
    assert result.value == ["PO", "QD", "PRN"]
    assert validate_sig_tokens("PO QD 💊").ok is False
    assert validate_sig_tokens("PO " + "X" * 17).ok is False


def test_sig_tokens_cap_count():
    raw = " ".join(["PO"] * (MAX_SIG_TOKENS + 1))
    assert validate_sig_tokens(raw).ok is False


def test_inventory_entry_returns_clean_payload():
    result = validate_inventory_entry("  Lipitor  ", "2027-03-15")
    assert result.ok is True
    assert result.value == {"drug": "Lipitor", "exp_date": "2027-03-15"}


def test_inventory_entry_rejects_bad_date():
    result = validate_inventory_entry("Lipitor", "2027-13-01")
    assert result.ok is False
    assert "date" in result.error.lower()


def test_partial_fill_returns_typed_payload():
    result = validate_partial_fill("Adderall", "30", "J. Doe", "2026-05-20")
    assert result.ok is True
    assert result.value == {
        "drug": "Adderall",
        "qty_owed": 30,
        "patient": "J. Doe",
        "date": "2026-05-20",
    }


def test_partial_fill_rejects_missing_patient_and_bad_qty():
    assert validate_partial_fill("Adderall", "abc", "J. Doe", "2026-05-20").ok is False
    assert validate_partial_fill("Adderall", "30", " ", "2026-05-20").ok is False


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
