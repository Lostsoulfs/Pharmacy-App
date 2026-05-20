#!/usr/bin/env python3
"""Logic-core regression — 29 assertions across the 11 S2 helpers.

Headless. No tkinter, no DB. Import-based (the modular refactor lets
this `import` the logic module directly instead of regex-extracting
from a monolith).

Run: python tests/test_logic.py    -> "Regression: 29/29 PASS"
Exit code 0 on full pass, 1 on any failure.

Coverage mirrors 04_TRACEABILITY_MATRIX:
  hash_pin 1, calc_insulin_logic 4, verify_dea_logic 4,
  calc_days_supply_logic 3, normalize_answer 2, answer_matches 2,
  is_strong_pin 3, dea_registrant_type 2, calc_crcl_cockcroft_gault 3,
  calc_bsa_mosteller 2, calc_peds_dose 3.
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

_passed = 0
_failed = 0


def check(test_id, condition):
    global _passed, _failed
    if condition:
        _passed += 1
    else:
        _failed += 1
        print("  FAIL %s" % test_id)


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


# --- hash_pin (1) ---
check("L-HP-01", hash_pin("1234") == hashlib.sha256(b"1234").hexdigest())

# --- calc_insulin_logic (4) ---
check("L-INS-01", calc_insulin_logic(10, 10, 100) == 100)
check("L-INS-02 priming", calc_insulin_logic(10, 10, 100,
                                             priming_units_per_day=10) == 50)
check("L-INS-03 nonpos", raises_valueerror(calc_insulin_logic, 0, 10, 100))
check("L-INS-04 nonnum", raises_valueerror(calc_insulin_logic, "x", 10, 100))

# --- verify_dea_logic (4) ---
check("L-DEA-01 valid", verify_dea_logic("AB1234563") is True)
check("L-DEA-02 bad checksum", verify_dea_logic("AB1234560") is False)
check("L-DEA-03 bad length", verify_dea_logic("AB123") is False)
check("L-DEA-04 lowercase", verify_dea_logic("ab1234563") is True)

# --- calc_days_supply_logic (3) ---
check("L-DS-01", calc_days_supply_logic(30, 1) == 30)
check("L-DS-02 floor", calc_days_supply_logic(100, 3) == 33)
check("L-DS-03 nonpos", raises_valueerror(calc_days_supply_logic, 0, 1))

# --- normalize_answer (2) ---
check("L-NA-01 none", normalize_answer(None) == "")
check("L-NA-02 normalize",
      normalize_answer("  Hydro-Chloro/Thiazide  ") == "hydro chloro thiazide")

# --- answer_matches (2) ---
check("L-AM-01 match", answer_matches("atorvastatin", "Atorvastatin") is True)
check("L-AM-02 none", answer_matches(None, "Atorvastatin") is False)

# --- is_strong_pin (3) ---
check("L-PIN-01 strong", is_strong_pin("4729")[0] is True)
check("L-PIN-02 repeated", is_strong_pin("1111")[0] is False)
check("L-PIN-03 sequential", is_strong_pin("1234")[0] is False)

# --- dea_registrant_type (2) ---
check("L-DRT-01 prescriber",
      dea_registrant_type("AB1234563") == ("Practitioner / Hospital", True))
check("L-DRT-02 manufacturer",
      dea_registrant_type("F1234563") == ("Manufacturer", False))

# --- calc_crcl_cockcroft_gault (3) ---
check("L-CG-01 male", near(calc_crcl_cockcroft_gault(40, 80, 1.0), 111.1))
check("L-CG-02 female",
      near(calc_crcl_cockcroft_gault(40, 80, 1.0, is_female=True), 94.4))
check("L-CG-03 bad scr",
      raises_valueerror(calc_crcl_cockcroft_gault, 40, 80, 0))

# --- calc_bsa_mosteller (2) ---
check("L-BSA-01", near(calc_bsa_mosteller(170, 70), 1.82))
check("L-BSA-02 bad height", raises_valueerror(calc_bsa_mosteller, 0, 70))

# --- calc_peds_dose (3) ---
_mg, _ml = calc_peds_dose(18, 90, 2, 50)
check("L-PD-01", near(_mg, 810.0) and near(_ml, 16.2))
check("L-PD-02 bad weight", raises_valueerror(calc_peds_dose, 0, 90, 2, 50))
_mg2, _ml2 = calc_peds_dose(10, 40, 4, 25)
check("L-PD-03", near(_mg2, 100.0) and near(_ml2, 4.0))


_total = _passed + _failed
print("Regression: %d/%d PASS" % (_passed, _total))
sys.exit(0 if _failed == 0 else 1)
