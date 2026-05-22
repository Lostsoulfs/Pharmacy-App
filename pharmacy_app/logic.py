"""Pure logic core — audited v13 logic + EARS corrections.

Headlessly testable. No tkinter, no sqlite dependency. calculate_weight
takes a caller-supplied DB connection so this module itself stays
import-clean.
"""

import hashlib
import math
from datetime import datetime


def hash_pin(pin_string):
    """EARS L-HP-01. Unchanged from audited v13 (40/40 GREEN)."""
    return hashlib.sha256(pin_string.encode()).hexdigest()


def calc_insulin_logic(daily_units, total_ml, concentration,
                       priming_units_per_day=0):
    """EARS L-INS-01..04 (+ F-06 fix, 2026-05-19).

    F-06 (domain expert, Nathan, pharmacist 2026-05-19): insulin pens
    waste ~2 units per injection on priming. Original formula
    ignored this and over-estimated days supply.

    New formula: days = floor(total_ml * concentration /
                              (daily_units + priming_units_per_day))

    priming_units_per_day defaults to 0 for backwards compat with
    vial calculations. For pens, pharmacist enters
    priming_per_injection x injections_per_day.

    Corrections preserved:
    - C02 (F-02): reject non-positive total_ml / concentration
    - Numeric-coercion guard separated from value validation
    - Contract preserved (raises ValueError on bad input)
    - Returns int floor (round-down, ext-verified)"""
    try:
        daily = float(daily_units)
        total = float(total_ml)
        conc = float(concentration)
        priming = float(priming_units_per_day)
    except (ValueError, TypeError):
        raise ValueError("Invalid numeric inputs.")
    # FUZZ-02: float('nan')/float('inf') parse OK but defeat every
    # <=/> bounds check below, so reject non-finite values up front.
    if not all(math.isfinite(v) for v in (daily, total, conc, priming)):
        raise ValueError("Invalid numeric inputs.")
    if daily <= 0:
        raise ValueError("Daily units must be greater than zero.")
    if total <= 0 or conc <= 0:
        raise ValueError("Total mL and concentration must be > 0.")
    if priming < 0:
        raise ValueError("Priming units cannot be negative.")
    # T7.18 / F-07 — bounds. Reject inputs > 1e6 (float-nonsense
    # territory); cap output at 3650 days (10 years).
    if max(daily, total, conc, priming) > 1e6:
        raise ValueError("Input out of plausible range.")
    effective_daily = daily + priming
    days = int((total * conc) / effective_daily)
    if days > 3650:
        raise ValueError(
            "Result implausible (> 10 years). Check inputs.")
    return days


def verify_dea_logic(dea):
    """EARS L-DEA-01..04.
    Correction C04 (F-05): ASCII-only letter/digit checks (was
    Unicode-aware isalpha/isdigit). Checksum algorithm unchanged —
    externally verified correct against 5 sources."""
    if not dea or not isinstance(dea, str):
        return False
    dea = dea.strip().upper()
    if len(dea) != 9:
        return False
    letters, digits = dea[:2], dea[2:]
    if not all('A' <= c <= 'Z' for c in letters):
        return False
    if not all('0' <= c <= '9' for c in digits):
        return False
    nums = [int(c) for c in digits]
    step1 = nums[0] + nums[2] + nums[4]
    step2 = (nums[1] + nums[3] + nums[5]) * 2
    check = str(step1 + step2)[-1]
    return check == dea[-1]


def calc_peds_dose(weight_kg, mg_per_kg_per_day, doses_per_day,
                   concentration_mg_per_ml):
    """T7.23. Pediatric weight-based dose to mL-per-dose.

    Workflow: 'Amoxicillin 90 mg/kg/day BID, child 18 kg,
    250 mg/5 mL suspension' -> mL per dose.

    Steps:
      total_mg_per_day = weight_kg x mg_per_kg_per_day
      mg_per_dose      = total_mg_per_day / doses_per_day
      mL_per_dose      = mg_per_dose / concentration_mg_per_ml

    Returns (mg_per_dose, mL_per_dose) both rounded to 2 decimals.
    Raises ValueError on bad input or implausible bounds.

    Concentration_mg_per_ml expects e.g. 50 for a '250 mg per 5 mL'
    suspension (250/5 = 50). Pharmacist does the division up front.
    No internal unit conversion."""
    try:
        wt = float(weight_kg)
        mkd = float(mg_per_kg_per_day)
        d = float(doses_per_day)
        conc = float(concentration_mg_per_ml)
    except (ValueError, TypeError):
        raise ValueError("Invalid numeric inputs.")
    if not all(math.isfinite(v) for v in (wt, mkd, d, conc)):  # FUZZ-02
        raise ValueError("Invalid numeric inputs.")
    if wt <= 0 or wt > 200:
        raise ValueError("Weight must be 0 < weight <= 200 kg.")
    if mkd <= 0 or mkd > 1000:
        raise ValueError("mg/kg/day must be 0 < x <= 1000.")
    if d <= 0 or d > 24 or not d.is_integer():
        raise ValueError(
            "Doses/day must be a whole number, 0 < n <= 24.")
    if conc <= 0 or conc > 1000:
        raise ValueError(
            "Concentration must be 0 < mg/mL <= 1000.")
    total_mg = wt * mkd
    mg_per_dose = total_mg / d
    ml_per_dose = mg_per_dose / conc
    return round(mg_per_dose, 2), round(ml_per_dose, 2)


def calc_bsa_mosteller(height_cm, weight_kg):
    """T7.22. Body Surface Area via Mosteller formula (NEJM 1987;
    widely used for chemotherapy and pediatric dose calculation;
    FDA-cited):

      BSA (m2) = sqrt((height_cm x weight_kg) / 3600)

    Returns float rounded to 2 decimals. Raises ValueError on bad
    input or implausible bounds."""
    try:
        h = float(height_cm)
        w = float(weight_kg)
    except (ValueError, TypeError):
        raise ValueError("Invalid numeric inputs.")
    if not all(math.isfinite(v) for v in (h, w)):  # FUZZ-02
        raise ValueError("Invalid numeric inputs.")
    if h <= 0 or h > 300:
        raise ValueError("Height must be 0 < height <= 300 cm.")
    if w <= 0 or w > 500:
        raise ValueError("Weight must be 0 < weight <= 500 kg.")
    return round(math.sqrt((h * w) / 3600.0), 2)


def calc_crcl_cockcroft_gault(age, weight_kg, serum_cr_mg_dl, is_female=False):
    """T7.21. Cockcroft-Gault creatinine clearance estimate.

    Formula (Cockcroft & Gault, Nephron 1976; widely cited and used
    by FDA for renal dose adjustment):

      CrCl (mL/min) = [(140 - age) x weight_kg] / (72 x SCr)
                     x 0.85 if female

    Returns float CrCl rounded to 1 decimal. Raises ValueError on
    bad input or implausible result. Note this is an ESTIMATE — not
    a substitute for measured CrCl, and not validated in pediatrics,
    extremes of weight, or unstable renal function. Pharmacist
    judgment required."""
    try:
        age_y = float(age)
        wt = float(weight_kg)
        scr = float(serum_cr_mg_dl)
    except (ValueError, TypeError):
        raise ValueError("Invalid numeric inputs.")
    if not all(math.isfinite(v) for v in (age_y, wt, scr)):  # FUZZ-02
        raise ValueError("Invalid numeric inputs.")
    if age_y <= 0 or age_y > 130:
        raise ValueError("Age must be 0 < age <= 130 years.")
    if wt <= 0 or wt > 500:
        raise ValueError("Weight must be 0 < weight <= 500 kg.")
    if scr <= 0 or scr > 30:
        raise ValueError("Serum creatinine must be 0 < SCr <= 30 mg/dL.")
    crcl = ((140.0 - age_y) * wt) / (72.0 * scr)
    if is_female:
        crcl *= 0.85
    return round(crcl, 1)


def dea_registrant_type(dea):
    """T7.20. Return (type_label, is_prescriber) tuple for a DEA
    number based on the first-letter prefix per DEA Diversion Control
    registrant codes (21 CFR 1301). Returns (None, False) if input
    is malformed.

    Prefix codes (cited from DEA Practitioner's Manual):
      A / B / G  -> Practitioner / Hospital (prescriber)
      M          -> Mid-level practitioner: NP, PA, etc (prescriber)
      F          -> Manufacturer (NOT a prescriber)
      P / R      -> Distributor / Researcher (NOT a prescriber)
      X          -> Suboxone / DATA-2000 waivered practitioner
                    (prescriber, narrow scope)
      Other      -> Unknown / unmapped
    """
    if not dea or not isinstance(dea, str):
        return (None, False)
    cleaned = dea.strip().upper()
    if len(cleaned) < 1:
        return (None, False)
    prefix = cleaned[0]
    mapping = {
        "A": ("Practitioner / Hospital", True),
        "B": ("Practitioner / Hospital", True),
        "G": ("Practitioner / Hospital", True),
        "M": ("Mid-Level Practitioner (NP/PA)", True),
        "F": ("Manufacturer", False),
        "P": ("Distributor / Researcher", False),
        "R": ("Researcher", False),
        "X": ("DATA-2000 / Suboxone Practitioner", True),
    }
    return mapping.get(prefix, ("Unknown prefix", False))


def calc_days_supply_logic(quantity, units_per_day):
    """EARS L-DS-01/02 (+ F-07 fix, 2026-05-19).
    int() floor = round-down = dominant billing convention.
    F-07: reject inputs > 1e6 and outputs > 3650 days (10 years)."""
    try:
        qty = float(quantity)
        daily = float(units_per_day)
    except (ValueError, TypeError):
        raise ValueError("Invalid quantity or daily-use value.")
    if not all(math.isfinite(v) for v in (qty, daily)):  # FUZZ-02
        raise ValueError("Invalid quantity or daily-use value.")
    if qty <= 0 or daily <= 0:
        raise ValueError("Invalid quantity or daily-use value.")
    if max(qty, daily) > 1e6:
        raise ValueError("Input out of plausible range.")
    days = int(qty / daily)
    if days > 3650:
        raise ValueError(
            "Result implausible (> 10 years). Check inputs.")
    return days


def normalize_answer(value):
    """EARS L-NA-01/02.
    Correction C03 (F-03): None is treated as absent (empty string),
    NOT coerced to the literal token 'none'."""
    if value is None:
        return ""
    return " ".join(
        str(value).strip().lower().replace("/", " ").replace("-", " ").split()
    )


def answer_matches(user_value, correct_value):
    """EARS L-AM-01..04. Logic unchanged; None now flows to False via
    the corrected normalize_answer (empty -> not user_norm -> False)."""
    user_norm = normalize_answer(user_value)
    correct_norm = normalize_answer(correct_value)
    if not user_norm:
        return False
    if user_norm == correct_norm:
        return True
    aliases = [
        normalize_answer(part)
        for part in str(correct_value).replace("/", ",").split(",")
    ]
    return user_norm in aliases


def is_strong_pin(new_pin, old_pin=None):
    """ADR-C07 / EARS L-PIN-*. Pure, headlessly testable.
    Returns (ok: bool, reason: str). Policy:
    - length >= 4
    - not equal to old_pin (no reuse of the current PIN)
    - not a single repeated character (0000, 1111, aaaa)
    - if all-digit: not a consecutive run, ascending or descending
      (1234, 2345, 0123, 4321, 9876 ...) — this also covers the old
      hardcoded '1234' case, so that special-case is removed."""
    if new_pin is None or len(new_pin) < 4:
        return False, "PIN must be at least 4 characters."
    if old_pin is not None and new_pin == old_pin:
        return False, "New PIN must differ from the current PIN."
    if len(set(new_pin)) == 1:
        return False, "PIN cannot be one repeated character."
    if new_pin.isdigit():
        d = [int(c) for c in new_pin]
        asc = all(d[i + 1] - d[i] == 1 for i in range(len(d) - 1))
        desc = all(d[i + 1] - d[i] == -1 for i in range(len(d) - 1))
        if asc or desc:
            return False, "PIN cannot be a sequential run of digits."
    return True, ""


def sm2_update(ease_factor, interval_days, repetitions, correct):
    """SM-2 spaced-repetition update (binary correct/incorrect variant).

    Reference: SuperMemo SM-2 algorithm (Piotr Wozniak, 1985).
    Simplified to binary correct/incorrect — no 0-5 quality grading;
    treats correct ~ quality 5, incorrect ~ quality 1.

    Pure function. Returns (new_ease_factor, new_interval_days,
    new_repetitions). Salvaged from the 2026-05-18 crunch bundle.

    Inputs (all tolerate None / junk — fall back to first-review state):
      ease_factor: float, current ease (2.5 on first review)
      interval_days: int, days until the next review
      repetitions: int, count of consecutive correct reviews
      correct: bool, was the answer correct?

    Algorithm:
      Correct:  reps 0 -> interval 1; reps 1 -> interval 6;
                reps >= 2 -> interval = round(prev_interval * ease);
                reps += 1; ease += 0.1
      Incorrect: interval = 0 (review again tomorrow); reps = 0;
                ease -= 0.2
      Ease is floored at 1.3 per classical SM-2."""
    try:
        ease = float(ease_factor) if ease_factor is not None else 2.5
        interval = int(interval_days) if interval_days is not None else 0
        reps = int(repetitions) if repetitions is not None else 0
    except (ValueError, TypeError):
        ease, interval, reps = 2.5, 0, 0
    if not math.isfinite(ease):
        ease = 2.5
    # ease/interval/reps are only ever written by this function or
    # NULL; enforce the invariants anyway (ease floored at the SM-2
    # 1.3 minimum, schedule non-negative) so a corrupt stored value
    # cannot produce a negative schedule that breaks random.choices.
    ease = max(1.3, ease)
    interval = max(0, interval)
    reps = max(0, reps)
    if correct:
        if reps == 0:
            new_interval = 1
        elif reps == 1:
            new_interval = 6
        else:
            new_interval = int(round(interval * ease))
        new_reps = reps + 1
        new_ease = ease + 0.1
    else:
        new_interval = 0
        new_reps = 0
        new_ease = ease - 0.2
    new_ease = max(1.3, new_ease)
    return new_ease, new_interval, new_reps


def calculate_weight(tech_name, drug_name, conn):
    """C06-EARS: Quiz mastery weighting. Per-user, per-drug.
    Returns int weight for random.choices(). Higher weight = higher
    probability of the drug appearing in hard mode.

    SM-2-aware (salvaged from the 2026-05-18 crunch bundle): when the
    card has a review timestamp, weight by how overdue it is. Falls
    back to the legacy miss-count weighting when the SRS columns are
    NULL (a card seen only under the pre-SRS schema).

    SM-2 path (last_reviewed populated):
      overdue_days = days_since_reviewed - interval_days
      overdue (>= 0): weight = min(50, 10 + overdue_days * 2)
      not yet due:    weight = max(1, 10 + overdue_days)  [overdue < 0]

    Legacy fallback path (no SRS data):
      no stats:            weight = 10 (new card)
      stats with misses:   weight = 10 + 5 * missed_count
      stats, no misses:    weight = 1 (mastered)

    Note: DB is caller's responsibility; connection passed in for
    isolation. A DB-access failure falls back to base weight 10;
    errors in the weighting logic itself propagate (real bugs)."""
    try:
        stats = conn.execute(
            "SELECT correct, total, ease_factor, interval_days, "
            "last_reviewed, repetitions FROM MasteryStats "
            "WHERE tech_name=? AND drug_name=?",
            (tech_name, drug_name)
        ).fetchone()
    except Exception:
        # Swallow DB-access failures only — everything below is pure
        # logic, and a failure there is a real bug that must surface
        # rather than be masked as a base-weight result.
        return 10
    if not stats or stats["total"] == 0:
        return 10
    if stats["last_reviewed"]:
        try:
            last = datetime.fromisoformat(stats["last_reviewed"])
            days_since = (datetime.now() - last).days
            interval = int(stats["interval_days"] or 0)
            overdue = days_since - interval
            if overdue >= 0:
                return min(50, 10 + overdue * 2)
            return max(1, 10 + overdue)
        except (ValueError, TypeError):
            pass  # fall through to legacy path
    missed = stats["total"] - stats["correct"]
    if missed > 0:
        return 10 + (missed * 5)
    return 1
