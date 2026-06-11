#!/usr/bin/env python3
"""Edge-case and invariant tests for pharmacy_app.

Covers boundaries and combinatorial properties NOT fully exercised by
test_logic.py (29 example assertions) or test_data.py (data-layer tests).

Focus areas:
  - SM-2 monotonicity, convergence, NaN fallback, ease upper bound
  - Clinical calculators: age/SCr/height/weight monotonicity, bounds,
    female-factor precision, 3650-day cap, floor division convention
  - PIN strength: reuse, descending runs, alphanumeric, None
  - DEA: unicode rejection, length guards, X-prefix prescriber flag
  - normalize_answer / answer_matches: alias, case, empty, None correct
  - calculate_weight SRS path: overdue cap, not-due floor, ordering

Run:  pytest tests/test_edge_cases.py -q
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pharmacy_app.logic import (  # noqa: E402
    answer_matches,
    calc_bsa_mosteller,
    calc_crcl_cockcroft_gault,
    calc_days_supply_logic,
    calc_insulin_logic,
    calc_peds_dose,
    calculate_weight,
    dea_registrant_type,
    is_strong_pin,
    normalize_answer,
    sm2_update,
    verify_dea_logic,
)


# ── SM-2 algorithm edge cases ───────────────────────────────────────────────────

class TestSM2EdgeCases:
    def test_ease_floor_100_failures(self):
        """100 consecutive incorrect answers cannot push ease below 1.3."""
        ease, interval, reps = 1.3, 0, 0
        for _ in range(100):
            ease, interval, reps = sm2_update(ease, interval, reps, False)
        assert ease == 1.3

    def test_ease_monotone_on_correct(self):
        """Ease is non-decreasing for consecutive correct answers."""
        ease, interval, reps = 2.5, 0, 0
        prev = ease
        for _ in range(20):
            ease, interval, reps = sm2_update(ease, interval, reps, True)
            assert ease >= prev
            prev = ease

    def test_interval_monotone_from_reps2(self):
        """After reps ≥ 2, consecutive correct answers grow the interval."""
        # prime to reps=2 (intervals 1 → 6)
        ease, interval, reps = 2.5, 0, 0
        for _ in range(2):
            ease, interval, reps = sm2_update(ease, interval, reps, True)
        prev = interval
        for _ in range(10):
            ease, interval, reps = sm2_update(ease, interval, reps, True)
            assert interval >= prev
            prev = interval

    def test_convergence_20_correct_cycles(self):
        """20 consecutive correct answers from initial state → interval > 100."""
        ease, interval, reps = None, None, None
        for _ in range(20):
            ease, interval, reps = sm2_update(ease, interval, reps, True)
        assert interval > 100

    def test_ease_finite_after_1000_correct(self):
        """1000 correct answers: ease stays finite and ≤ 105."""
        ease, interval, reps = 2.5, 0, 0
        for _ in range(1000):
            ease, interval, reps = sm2_update(ease, interval, reps, True)
        assert math.isfinite(ease)
        assert ease <= 105.0

    def test_incorrect_resets_regardless_of_prior_reps(self):
        """After 50 correct, one incorrect resets interval=0 and reps=0."""
        ease, interval, reps = 2.5, 0, 0
        for _ in range(50):
            ease, interval, reps = sm2_update(ease, interval, reps, True)
        ease2, interval2, reps2 = sm2_update(ease, interval, reps, False)
        assert interval2 == 0
        assert reps2 == 0

    def test_nan_ease_falls_back_to_initial(self):
        """NaN ease produces a finite result (first-review path)."""
        ease, interval, reps = sm2_update(float("nan"), 10, 3, True)
        assert math.isfinite(ease)
        assert interval == 1


# ── Clinical calculator bounds and monotonicity ────────────────────────────

class TestClinicalCalcBounds:
    # CrCl — Cockcroft-Gault
    def test_crcl_age_130_valid(self):
        assert calc_crcl_cockcroft_gault(130, 80, 1.0) > 0

    def test_crcl_age_131_raises(self):
        with pytest.raises(ValueError):
            calc_crcl_cockcroft_gault(131, 80, 1.0)

    def test_crcl_decreasing_with_age(self):
        young = calc_crcl_cockcroft_gault(30, 80, 1.0)
        mid   = calc_crcl_cockcroft_gault(60, 80, 1.0)
        old   = calc_crcl_cockcroft_gault(90, 80, 1.0)
        assert young > mid > old

    def test_crcl_decreasing_with_scr(self):
        low_scr  = calc_crcl_cockcroft_gault(50, 70, 0.8)
        high_scr = calc_crcl_cockcroft_gault(50, 70, 2.0)
        assert low_scr > high_scr

    def test_crcl_female_factor_085(self):
        """Female CrCl is exactly 0.85 × male for all valid inputs."""
        male   = calc_crcl_cockcroft_gault(40, 80, 1.0, is_female=False)
        female = calc_crcl_cockcroft_gault(40, 80, 1.0, is_female=True)
        assert abs(female - male * 0.85) < 0.1

    # BSA — Mosteller
    def test_bsa_monotone_with_height(self):
        assert calc_bsa_mosteller(180, 70) > calc_bsa_mosteller(160, 70)

    def test_bsa_monotone_with_weight(self):
        assert calc_bsa_mosteller(170, 90) > calc_bsa_mosteller(170, 60)

    @pytest.mark.parametrize("h,w", [
        (50, 3), (170, 70), (200, 120), (100, 40),
    ])
    def test_bsa_plausibility(self, h, w):
        """All valid inputs produce BSA in [0.10, 4.00] m²."""
        bsa = calc_bsa_mosteller(h, w)
        assert 0.10 <= bsa <= 4.00, f"h={h} w={w} → BSA={bsa}"

    # Insulin / days-supply caps
    def test_insulin_3650_day_cap_raises(self):
        """Inputs that would exceed 10 years are rejected."""
        with pytest.raises(ValueError):
            calc_insulin_logic(0.001, 1000, 1000)

    def test_days_supply_floor_31_div_3(self):
        """31 / 3 = 10 (floor), not 11 (ceil) or 10.33 (round)."""
        assert calc_days_supply_logic(31, 3) == 10

    def test_days_supply_exact_divisible(self):
        assert calc_days_supply_logic(30, 3) == 10

    # Peds dose
    def test_peds_fractional_doses_rejected(self):
        with pytest.raises(ValueError):
            calc_peds_dose(18, 90, 2.5, 50)


# ── PIN strength extended cases ───────────────────────────────────────────────

class TestPinStrength:
    def test_reuse_rejected(self):
        ok, reason = is_strong_pin("4729", old_pin="4729")
        assert not ok
        assert "differ" in reason.lower()

    def test_descending_sequence_rejected(self):
        assert is_strong_pin("4321")[0] is False

    def test_ascending_5_digit_rejected(self):
        assert is_strong_pin("12345")[0] is False

    def test_alphanumeric_accepted(self):
        assert is_strong_pin("ab12")[0] is True

    def test_length_3_rejected(self):
        ok, reason = is_strong_pin("123")
        assert not ok
        assert "4" in reason  # mentions minimum length 4

    def test_repeated_alpha_rejected(self):
        assert is_strong_pin("aaaa")[0] is False

    def test_none_rejected(self):
        assert is_strong_pin(None)[0] is False

    def test_different_old_pin_passes(self):
        """new != old and otherwise strong → accepted."""
        ok, _ = is_strong_pin("4729", old_pin="1111")
        assert ok


# ── DEA validation edge cases ──────────────────────────────────────────────────

class TestDEAValidation:
    def test_x_prefix_is_prescriber(self):
        _, is_prescriber = dea_registrant_type("XY1234563")
        assert is_prescriber is True

    def test_f_prefix_not_prescriber(self):
        _, is_prescriber = dea_registrant_type("FB1234563")
        assert is_prescriber is False

    def test_lowercase_normalised(self):
        assert verify_dea_logic("ab1234563") is True

    def test_unicode_letter_rejected(self):
        assert verify_dea_logic("ÄB1234563") is False

    def test_8_chars_too_short(self):
        assert verify_dea_logic("AB123456") is False

    def test_10_chars_too_long(self):
        assert verify_dea_logic("AB12345630") is False

    def test_none_input(self):
        assert verify_dea_logic(None) is False
        assert dea_registrant_type(None) == (None, False)


# ── normalize_answer / answer_matches ─────────────────────────────────────

class TestAnswerNormalization:
    def test_slash_and_dash_to_spaces(self):
        assert normalize_answer("Hydro-Chloro/Thiazide") == "hydro chloro thiazide"

    def test_extra_whitespace_collapsed(self):
        assert normalize_answer("  drug   name  ") == "drug name"

    def test_alias_match_hctz(self):
        """HCTZ alias accepted for Hydrochlorothiazide/HCTZ."""
        assert answer_matches("hctz", "Hydrochlorothiazide/HCTZ") is True

    def test_empty_string_never_matches(self):
        assert answer_matches("", "Drug") is False

    def test_case_insensitive(self):
        assert answer_matches("ATORVASTATIN", "atorvastatin") is True

    def test_none_user_answer(self):
        assert answer_matches(None, "Drug") is False

    def test_none_correct_normalises_to_empty(self):
        """None correct-value normalises to '' — no real answer matches it."""
        assert answer_matches("Drug", None) is False


# ── calculate_weight SRS-aware paths ────────────────────────────────────────

class TestCalculateWeightSRS:
    @pytest.fixture
    def db(self, tmp_path, monkeypatch):
        import pharmacy_app.data as D
        monkeypatch.setattr(D, "DB_FILE", str(tmp_path / "srs_test.db"))
        monkeypatch.setenv("HOME", str(tmp_path))
        D.init_db()
        return D

    def test_overdue_40d_capped_at_50(self, db):
        from datetime import datetime, timedelta
        long_ago = (datetime.now() - timedelta(days=40)).isoformat(timespec="seconds")
        db.db_upsert_mastery_stats("Alice", "Lipitor", 5, 5, 2.5, 1, 3, long_ago)
        conn = db.get_db_connection()
        try:
            w = calculate_weight("Alice", "Lipitor", conn)
        finally:
            conn.close()
        # overdue = 40-1 = 39 → min(50, 10+39×2) = min(50, 88) = 50
        assert w == 50

    def test_not_due_interval3_returns_7(self, db):
        """days_since=0, interval=3 → overdue=-3 → max(1, 10-3) = 7.

        Result of 7 (not 1) proves the SRS branch ran, not the legacy
        all-correct fallback which would also return 1.
        """
        from datetime import datetime
        just_now = datetime.now().isoformat(timespec="seconds")
        db.db_upsert_mastery_stats("Alice", "Nexium", 5, 5, 2.5, 3, 2, just_now)
        conn = db.get_db_connection()
        try:
            w = calculate_weight("Alice", "Nexium", conn)
        finally:
            conn.close()
        assert w == 7

    def test_overdue_outranks_not_due(self, db):
        """Overdue card always has higher weight than a not-yet-due card."""
        from datetime import datetime, timedelta
        long_ago = (datetime.now() - timedelta(days=40)).isoformat(timespec="seconds")
        just_now = datetime.now().isoformat(timespec="seconds")
        db.db_upsert_mastery_stats("Alice", "Lipitor", 5, 5, 2.5, 1,  3, long_ago)
        db.db_upsert_mastery_stats("Alice", "Zoloft",  5, 5, 2.5, 30, 3, just_now)
        conn = db.get_db_connection()
        try:
            overdue = calculate_weight("Alice", "Lipitor", conn)
            not_due = calculate_weight("Alice", "Zoloft", conn)
        finally:
            conn.close()
        assert overdue > not_due


if __name__ == "__main__":
    import pytest as _pt
    sys.exit(_pt.main([__file__, "-q"]))
