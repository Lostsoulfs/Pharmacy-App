#!/usr/bin/env python3
"""Logic-core regression — 29 example assertions across the 11 S2 helpers.

pytest-native (migrated from the old check()/sys.exit harness so the
whole suite — examples + property tests + data tests — runs under one
`pytest` command and feeds mutation testing).

Headless: no tkinter, no DB. Each function below groups the test IDs
from 04_TRACEABILITY_MATRIX (L-HP-01 .. L-PD-03).

Run under pytest:   pytest tests/test_logic.py -q
Run standalone:     python tests/test_logic.py
"""

import os
import sys
import hashlib

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pharmacy_app.logic import (  # noqa: E402
    hash_pin, calc_insulin_logic, verify_dea_logic, calc_days_supply_logic,
    normalize_answer, answer_matches, is_strong_pin, dea_registrant_type,
    calc_crcl_cockcroft_gault, calc_bsa_mosteller, calc_peds_dose,
)


def raises_valueerror(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
        return False
    except ValueError:
        return True
    except Exception:
        return False


def near(a, b, tol=1e-6):
    return abs(a - b) <= tol


# --- hash_pin (1) ----------------------------------------------------
def test_hash_pin():
    # L-HP-01
    assert hash_pin("1234") == hashlib.sha256(b"1234").hexdigest()


# --- calc_insulin_logic (4) -----------------------------------------
def test_calc_insulin_logic():
    assert calc_insulin_logic(10, 10, 100) == 100                # L-INS-01
    assert calc_insulin_logic(10, 10, 100,
                              priming_units_per_day=10) == 50    # L-INS-02
    assert raises_valueerror(calc_insulin_logic, 0, 10, 100)     # L-INS-03
    assert raises_valueerror(calc_insulin_logic, "x", 10, 100)   # L-INS-04


# --- verify_dea_logic (4) -------------------------------------------
def test_verify_dea_logic():
    assert verify_dea_logic("AB1234563") is True                 # L-DEA-01
    assert verify_dea_logic("AB1234560") is False                # L-DEA-02
    assert verify_dea_logic("AB123") is False                    # L-DEA-03
    assert verify_dea_logic("ab1234563") is True                 # L-DEA-04


# --- calc_days_supply_logic (3) -------------------------------------
def test_calc_days_supply_logic():
    assert calc_days_supply_logic(30, 1) == 30                   # L-DS-01
    assert calc_days_supply_logic(100, 3) == 33                  # L-DS-02
    assert raises_valueerror(calc_days_supply_logic, 0, 1)       # L-DS-03


# --- normalize_answer (2) -------------------------------------------
def test_normalize_answer():
    assert normalize_answer(None) == ""                          # L-NA-01
    assert (normalize_answer("  Hydro-Chloro/Thiazide  ")
            == "hydro chloro thiazide")                          # L-NA-02


# --- answer_matches (2) ---------------------------------------------
def test_answer_matches():
    assert answer_matches("atorvastatin", "Atorvastatin") is True  # L-AM-01
    assert answer_matches(None, "Atorvastatin") is False           # L-AM-02


# --- is_strong_pin (3) ----------------------------------------------
def test_is_strong_pin():
    assert is_strong_pin("4729")[0] is True                      # L-PIN-01
    assert is_strong_pin("1111")[0] is False                     # L-PIN-02
    assert is_strong_pin("1234")[0] is False                     # L-PIN-03


# --- dea_registrant_type (2) ----------------------------------------
def test_dea_registrant_type():
    assert dea_registrant_type("AB1234563") == (
        "Practitioner / Hospital", True)                         # L-DRT-01
    assert dea_registrant_type("F1234563") == (
        "Manufacturer", False)                                   # L-DRT-02


# --- calc_crcl_cockcroft_gault (3) ----------------------------------
def test_calc_crcl_cockcroft_gault():
    assert near(calc_crcl_cockcroft_gault(40, 80, 1.0), 111.1)   # L-CG-01
    assert near(calc_crcl_cockcroft_gault(40, 80, 1.0,
                                          is_female=True), 94.4)  # L-CG-02
    assert raises_valueerror(
        calc_crcl_cockcroft_gault, 40, 80, 0)                    # L-CG-03


# --- calc_bsa_mosteller (2) -----------------------------------------
def test_calc_bsa_mosteller():
    assert near(calc_bsa_mosteller(170, 70), 1.82)               # L-BSA-01
    assert raises_valueerror(calc_bsa_mosteller, 0, 70)          # L-BSA-02


# --- calc_peds_dose (3) ---------------------------------------------
def test_calc_peds_dose():
    mg, ml = calc_peds_dose(18, 90, 2, 50)
    assert near(mg, 810.0) and near(ml, 16.2)                    # L-PD-01
    assert raises_valueerror(calc_peds_dose, 0, 90, 2, 50)       # L-PD-02
    mg2, ml2 = calc_peds_dose(10, 40, 4, 25)
    assert near(mg2, 100.0) and near(ml2, 4.0)                   # L-PD-03


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
