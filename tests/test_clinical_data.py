#!/usr/bin/env python3
"""Structural integrity tests for the clinical_data.py datasets.

These do NOT check clinical correctness (that is the audit's job) —
they lock the data *shape* so a future edit can't silently break a
panel that renders these structures. Headless: no tkinter, no DB.

Run under pytest:   pytest tests/test_clinical_data.py -q
Run standalone:     python tests/test_clinical_data.py
"""

import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pharmacy_app.clinical_data import (  # noqa: E402
    RED_FLAGS, LASA_PAIRS, SIG_ABBREVIATIONS, COMMON_RX_FLAGS,
    BRAND_GENERIC, VACCINES,
)


def _nonempty_str(value):
    return isinstance(value, str) and value.strip() != ""


def _check_dicts(rows, keys):
    assert isinstance(rows, list) and rows
    for row in rows:
        assert isinstance(row, dict)
        assert set(row) == set(keys)
        for key in keys:
            assert _nonempty_str(row[key]), (key, row)


def test_brand_generic_shape():
    _check_dicts(BRAND_GENERIC, ("brand", "generic", "drug_class"))
    assert len(BRAND_GENERIC) >= 200


def test_brand_generic_no_duplicate_pairs():
    pairs = [(r["brand"], r["generic"]) for r in BRAND_GENERIC]
    assert len(pairs) == len(set(pairs))


def test_red_flags_shape():
    _check_dicts(RED_FLAGS, ("q", "a", "rationale"))
    assert len(RED_FLAGS) >= 10


def test_lasa_pairs_shape():
    _check_dicts(LASA_PAIRS, ("q", "a", "rationale"))
    assert len(LASA_PAIRS) >= 10


def test_vaccines_shape():
    _check_dicts(VACCINES, ("vaccine", "ages", "schedule", "notes"))
    assert len(VACCINES) >= 10


def test_sig_abbreviations_shape():
    assert isinstance(SIG_ABBREVIATIONS, dict) and SIG_ABBREVIATIONS
    for abbr, meaning in SIG_ABBREVIATIONS.items():
        assert _nonempty_str(abbr) and _nonempty_str(meaning)


def test_common_rx_flags_shape():
    assert isinstance(COMMON_RX_FLAGS, list) and COMMON_RX_FLAGS
    for entry in COMMON_RX_FLAGS:
        assert isinstance(entry, tuple) and len(entry) == 2
        assert all(_nonempty_str(field) for field in entry)


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
