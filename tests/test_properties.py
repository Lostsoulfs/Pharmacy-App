#!/usr/bin/env python3
"""Property-based / fuzz tests for pharmacy_app.logic (Hypothesis).

Where test_logic.py checks fixed examples, this file checks *properties*
that must hold for every input Hypothesis can generate. It hammers the
edges of the bounds checks in logic.py and shrinks any failure to a
minimal reproducing case.

Run:  pytest tests/test_properties.py -q
Deps: pip install hypothesis pytest
"""

import os
import sys
import math
import hashlib

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hypothesis import given, strategies as st  # noqa: E402

from pharmacy_app.logic import (  # noqa: E402
    hash_pin, calc_insulin_logic, verify_dea_logic, calc_days_supply_logic,
    normalize_answer, answer_matches, is_strong_pin, dea_registrant_type,
    calc_crcl_cockcroft_gault, calc_bsa_mosteller, calc_peds_dose,
    sm2_update,
)

# Strategies ----------------------------------------------------------
utf8_text = st.text(st.characters(codec="utf-8"))
any_value = st.one_of(
    st.none(), utf8_text, st.integers(),
    st.floats(allow_nan=True, allow_infinity=True), st.booleans(),
)
# Numbers that exercise the coercion guards: real numbers + junk types.
numeric_or_junk = st.one_of(
    st.integers(), st.floats(allow_nan=True, allow_infinity=True),
    st.text(), st.none(),
)


def _value_error_only(fn, *args):
    """Call fn; pass if it returns OR raises ValueError. Any other
    exception type is a bug — re-raise it so Hypothesis reports it."""
    try:
        return fn(*args), True
    except ValueError:
        return None, False


# --- hash_pin --------------------------------------------------------
@given(utf8_text)
def test_hash_pin_is_sha256_and_deterministic(pin):
    h1 = hash_pin(pin)
    h2 = hash_pin(pin)
    assert h1 == h2                                  # deterministic
    assert h1 == hashlib.sha256(pin.encode()).hexdigest()
    assert len(h1) == 64                             # always 64 hex
    assert all(c in "0123456789abcdef" for c in h1)


# --- calc_insulin_logic ---------------------------------------------
@given(numeric_or_junk, numeric_or_junk, numeric_or_junk, numeric_or_junk)
def test_insulin_never_raises_unexpected(daily, total, conc, priming):
    result, ok = _value_error_only(
        calc_insulin_logic, daily, total, conc, priming)
    if ok:
        assert isinstance(result, int)
        assert 0 <= result <= 3650               # output bounds hold


@given(st.floats(min_value=0.01, max_value=1e6),
       st.floats(min_value=0.01, max_value=1e6),
       st.floats(min_value=0.01, max_value=1e6))
def test_insulin_nonpositive_daily_rejected(total, conc, priming):
    _, ok = _value_error_only(calc_insulin_logic, 0, total, conc)
    assert not ok                                # daily=0 must raise


# --- calc_days_supply_logic -----------------------------------------
@given(numeric_or_junk, numeric_or_junk)
def test_days_supply_never_raises_unexpected(qty, daily):
    result, ok = _value_error_only(calc_days_supply_logic, qty, daily)
    if ok:
        assert isinstance(result, int)
        assert 0 <= result <= 3650


@given(st.floats(min_value=0.01, max_value=1e6),
       st.floats(min_value=0.01, max_value=1e6))
def test_days_supply_is_a_floor(qty, daily):
    result, ok = _value_error_only(calc_days_supply_logic, qty, daily)
    if ok:
        # floor: never reports more days than the raw division
        assert result <= (qty / daily) + 1e-9


# --- verify_dea_logic -----------------------------------------------
@given(st.one_of(utf8_text, st.none(), st.integers()))
def test_verify_dea_always_bool_never_raises(value):
    assert verify_dea_logic(value) in (True, False)


@given(st.from_regex(r"[A-Z]{2}", fullmatch=True),
       st.from_regex(r"[0-9]{6}", fullmatch=True))
def test_verify_dea_checksum_round_trip(letters, digits):
    nums = [int(c) for c in digits]
    step1 = nums[0] + nums[2] + nums[4]
    step2 = (nums[1] + nums[3] + nums[5]) * 2
    check = str(step1 + step2)[-1]
    # a correctly-computed check digit must verify True
    assert verify_dea_logic(letters + digits + check) is True
    # any other check digit must verify False
    wrong = str((int(check) + 1) % 10)
    assert verify_dea_logic(letters + digits + wrong) is False


# --- dea_registrant_type --------------------------------------------
@given(st.one_of(utf8_text, st.none(), st.integers()))
def test_dea_registrant_type_shape(value):
    result = dea_registrant_type(value)
    assert isinstance(result, tuple) and len(result) == 2
    assert isinstance(result[1], bool)


# --- calc_bsa_mosteller ---------------------------------------------
@given(numeric_or_junk, numeric_or_junk)
def test_bsa_never_raises_unexpected(h, w):
    result, ok = _value_error_only(calc_bsa_mosteller, h, w)
    if ok:
        # >= 0, not > 0: the bounds check only requires inputs > 0, so
        # physically tiny inputs round down to 0.00 (see FUZZ-01).
        assert isinstance(result, float) and result >= 0


# --- calc_crcl_cockcroft_gault --------------------------------------
@given(numeric_or_junk, numeric_or_junk, numeric_or_junk, st.booleans())
def test_crcl_never_raises_unexpected(age, wt, scr, is_female):
    result, ok = _value_error_only(
        calc_crcl_cockcroft_gault, age, wt, scr, is_female)
    if ok:
        # >= 0, not > 0: same loose-lower-bound issue as BSA (FUZZ-01).
        assert isinstance(result, float) and result >= 0


@given(st.floats(min_value=1, max_value=130),
       st.floats(min_value=1, max_value=500),
       st.floats(min_value=0.1, max_value=30))
def test_crcl_female_factor_lowers_result(age, wt, scr):
    male = calc_crcl_cockcroft_gault(age, wt, scr, is_female=False)
    female = calc_crcl_cockcroft_gault(age, wt, scr, is_female=True)
    assert female <= male                        # 0.85 factor applied


# --- calc_peds_dose -------------------------------------------------
@given(numeric_or_junk, numeric_or_junk, numeric_or_junk, numeric_or_junk)
def test_peds_dose_never_raises_unexpected(wt, mkd, d, conc):
    result, ok = _value_error_only(calc_peds_dose, wt, mkd, d, conc)
    if ok:
        assert isinstance(result, tuple) and len(result) == 2
        mg, ml = result
        assert mg >= 0 and ml >= 0
        assert math.isfinite(mg) and math.isfinite(ml)


# --- normalize_answer -----------------------------------------------
@given(any_value)
def test_normalize_answer_is_idempotent_and_clean(value):
    once = normalize_answer(value)
    assert isinstance(once, str)
    assert once == once.strip()                  # no edge whitespace
    assert once == once.lower()                  # always lowercase
    assert normalize_answer(once) == once        # idempotent


# --- answer_matches -------------------------------------------------
@given(st.one_of(st.none(), utf8_text), st.one_of(st.none(), utf8_text))
def test_answer_matches_returns_bool(user, correct):
    assert answer_matches(user, correct) in (True, False)


@given(utf8_text)
def test_answer_matches_reflexive_for_real_input(value):
    # if the value normalizes to something non-empty, it matches itself
    if normalize_answer(value):
        assert answer_matches(value, value) is True


# --- is_strong_pin --------------------------------------------------
@given(st.one_of(st.none(), utf8_text), st.one_of(st.none(), utf8_text))
def test_is_strong_pin_shape(new_pin, old_pin):
    ok, reason = is_strong_pin(new_pin, old_pin)
    assert isinstance(ok, bool) and isinstance(reason, str)
    if ok:
        assert reason == ""                      # accepted => no reason
    else:
        assert reason != ""                      # rejected => has reason


@given(st.text(max_size=3))
def test_is_strong_pin_rejects_short(new_pin):
    ok, _ = is_strong_pin(new_pin)
    assert ok is False                           # < 4 chars always fails


# --- mutation-testing-driven cases (mutmut found these gaps) --------
def test_is_strong_pin_sequential_variants():
    # kills the range(len-1) -> range(len-2) off-by-one mutant
    assert is_strong_pin("2345")[0] is False     # ascending run
    assert is_strong_pin("9876")[0] is False     # descending run
    assert is_strong_pin("1239")[0] is True      # ascending then breaks
    assert is_strong_pin("9870")[0] is True      # descending then breaks


def test_is_strong_pin_rejects_reuse():
    assert is_strong_pin("4827", old_pin="4827")[0] is False
    assert is_strong_pin("4827", old_pin="5193")[0] is True


def test_answer_matches_alias_branch():
    # the slash/comma alias path was never exercised by any test
    assert answer_matches("acetaminophen", "Tylenol/Acetaminophen") is True
    assert answer_matches("tylenol", "Tylenol/Acetaminophen") is True
    assert answer_matches("aspirin", "Tylenol/Acetaminophen") is False


def test_crcl_nonunity_creatinine():
    # every other CrCl test uses serum creatinine = 1.0, which makes a
    # 72*scr vs 72/scr formula error invisible (both give 72 at scr=1).
    # scr=2.0 distinguishes them: (140-60)*72 / (72*2) = 40.0.
    assert math.isclose(calc_crcl_cockcroft_gault(60, 72, 2.0), 40.0)
    assert math.isclose(
        calc_crcl_cockcroft_gault(60, 72, 2.0, is_female=True), 34.0)


def test_calculator_zero_lower_bounds_rejected():
    # exact-zero on the lower-bound guards (kills <=0 -> <0 mutants)
    for args in [
        (calc_crcl_cockcroft_gault, 40, 0, 1.0),     # weight 0
        (calc_crcl_cockcroft_gault, 0, 80, 1.0),     # age 0
        (calc_peds_dose, 18, 0, 2, 50),              # mg/kg/day 0
        (calc_peds_dose, 18, 90, 2, 0),              # concentration 0
        (calc_bsa_mosteller, 170, 0),                # weight 0
    ]:
        _, ok = _value_error_only(*args)
        assert not ok


def test_insulin_daily_one_is_valid():
    # daily=1 is valid (>0); kills the daily<=0 -> daily<=1 mutant
    assert calc_insulin_logic(1, 10, 100) == 1000


# --- sm2_update ------------------------------------------------------
# sm2_update only ever reads SRS state it previously wrote (or NULL):
# a finite ease >= 1.3, a non-negative interval, a non-negative reps.
# These strategies cover that real stored-state domain plus NULL.
sm2_ease = st.one_of(st.none(),
                     st.floats(min_value=1.3, max_value=100))
sm2_interval = st.one_of(st.none(), st.integers(min_value=0,
                                                max_value=10_000))
sm2_reps = st.one_of(st.none(), st.integers(min_value=0, max_value=1_000))


@given(sm2_ease, sm2_interval, sm2_reps, st.booleans())
def test_sm2_update_invariants_hold(ease, interval, reps, correct):
    new_ease, new_interval, new_reps = sm2_update(
        ease, interval, reps, correct)
    # ease floored at 1.3 and always a finite float
    assert isinstance(new_ease, float) and math.isfinite(new_ease)
    assert new_ease >= 1.3
    # interval and repetitions are non-negative ints
    assert isinstance(new_interval, int) and new_interval >= 0
    assert isinstance(new_reps, int) and new_reps >= 0
    # incorrect always resets the schedule; correct always advances reps
    if correct:
        assert new_reps >= 1
    else:
        assert new_reps == 0 and new_interval == 0


@given(st.floats(min_value=1.3, max_value=5.0),
       st.integers(min_value=0, max_value=10_000),
       st.integers(min_value=2, max_value=500))
def test_sm2_update_correct_grows_interval(ease, interval, reps):
    # for an established card (reps>=2) a correct answer never shortens
    # the interval — spaced repetition only stretches it out
    _, new_interval, _ = sm2_update(ease, interval, reps, True)
    assert new_interval >= interval


def test_dea_registrant_all_prefixes():
    # only A and F were tested before — B/G/M/P/R/X/unknown all open
    assert dea_registrant_type("B1234563")[1] is True
    assert dea_registrant_type("G1234563")[1] is True
    assert dea_registrant_type("M1234563") == (
        "Mid-Level Practitioner (NP/PA)", True)
    assert dea_registrant_type("P1234563") == (
        "Distributor / Researcher", False)
    assert dea_registrant_type("R1234563") == ("Researcher", False)
    assert dea_registrant_type("X1234563") == (
        "DATA-2000 / Suboxone Practitioner", True)
    assert dea_registrant_type("Z1234563") == ("Unknown prefix", False)
