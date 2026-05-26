#!/usr/bin/env python3
"""Pharmacy App diagnostic / debug runner.

Exercises every major logic and data function against a fresh temp DB
and prints a per-check [PASS]/[FAIL] summary.  No pytest or external
dependencies required — safe to run on-device with Pydroid 3.

Usage:
    python debug_run.py              # quiet (only FAILs shown)
    python debug_run.py --verbose    # show PASS lines too + DEBUG log
    python debug_run.py --no-data    # skip DB tests (logic only)

Exits 0 if all checks pass, 1 if any fail.
"""
import argparse
import logging
import math
import os
import shutil
import sys
import tempfile
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pharmacy_app.debug_log import setup as _setup_logging  # noqa: E402

# ---------------------------------------------------------------------------
# Minimal check/report harness
# ---------------------------------------------------------------------------

_PASS = 0
_FAIL = 0
_ERRORS = []
_VERBOSE = False


def check(label, condition, detail=""):
    global _PASS, _FAIL
    if condition:
        _PASS += 1
        if _VERBOSE:
            print(f"  [PASS] {label}")
    else:
        _FAIL += 1
        print(f"  [FAIL] {label}" + (f"\n         {detail}" if detail else ""))
        _ERRORS.append(label)
    return condition


def section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")


def run_safely(label, fn):
    """Run fn(); report uncaught exceptions as FAIL."""
    global _FAIL
    try:
        fn()
    except Exception as exc:
        _FAIL += 1
        print(f"  [FAIL] {label}: {type(exc).__name__}: {exc}")
        if _VERBOSE:
            traceback.print_exc()
        _ERRORS.append(label)


# ---------------------------------------------------------------------------
# Section 1 — Logic functions (headless, no DB)
# ---------------------------------------------------------------------------

def _test_logic():
    import hashlib
    from pharmacy_app.logic import (
        answer_matches,
        calc_bsa_mosteller,
        calc_crcl_cockcroft_gault,
        calc_days_supply_logic,
        calc_insulin_logic,
        calc_peds_dose,
        dea_registrant_type,
        hash_pin,
        is_strong_pin,
        normalize_answer,
        sm2_update,
        verify_dea_logic,
    )

    def raises(fn, *a, **kw):
        try:
            fn(*a, **kw)
            return False
        except ValueError:
            return True

    section("hash_pin")
    check("SHA-256 of '1234'",
          hash_pin("1234") == hashlib.sha256(b"1234").hexdigest())
    check("Different inputs produce different hashes",
          hash_pin("1234") != hash_pin("5678"))

    section("calc_days_supply_logic")
    check("30 / 1 = 30",         calc_days_supply_logic(30, 1) == 30)
    check("31 / 3 = 10 (floor)", calc_days_supply_logic(31, 3) == 10)
    check("100 / 3 = 33",        calc_days_supply_logic(100, 3) == 33)
    check("qty=0 raises",        raises(calc_days_supply_logic, 0, 1))
    check("daily=0 raises",      raises(calc_days_supply_logic, 30, 0))

    section("calc_bsa_mosteller")
    bsa = calc_bsa_mosteller(170, 70)
    check(f"170cm/70kg ≈ 1.82 (got {bsa})", abs(bsa - 1.82) < 0.01)
    check("Taller → larger BSA (same weight)",
          calc_bsa_mosteller(180, 70) > calc_bsa_mosteller(160, 70))
    check("Heavier → larger BSA (same height)",
          calc_bsa_mosteller(170, 90) > calc_bsa_mosteller(170, 60))
    check("height=0 raises", raises(calc_bsa_mosteller, 0, 70))
    for h, w in [(50, 3), (170, 70), (200, 120), (100, 40)]:
        b = calc_bsa_mosteller(h, w)
        check(f"BSA plausibility h={h} w={w}: {b}", 0.10 <= b <= 4.00)

    section("calc_crcl_cockcroft_gault")
    crcl_m = calc_crcl_cockcroft_gault(40, 80, 1.0)
    crcl_f = calc_crcl_cockcroft_gault(40, 80, 1.0, is_female=True)
    check(f"Male 40y/80kg/SCr1.0 ≈ 111.1 (got {crcl_m})", abs(crcl_m - 111.1) < 0.2)
    check(f"Female = 0.85 × male (got {crcl_f})", abs(crcl_f - crcl_m * 0.85) < 0.15)
    check("Older patient → lower CrCl",
          calc_crcl_cockcroft_gault(70, 80, 1.0) < calc_crcl_cockcroft_gault(40, 80, 1.0))
    check("Higher SCr → lower CrCl",
          calc_crcl_cockcroft_gault(50, 70, 2.0) < calc_crcl_cockcroft_gault(50, 70, 0.8))
    check("age=130 valid",     calc_crcl_cockcroft_gault(130, 80, 1.0) > 0)
    check("age=131 raises",    raises(calc_crcl_cockcroft_gault, 131, 80, 1.0))
    check("SCr=0 raises",      raises(calc_crcl_cockcroft_gault, 40, 80, 0))

    section("calc_peds_dose")
    mg, ml = calc_peds_dose(18, 90, 2, 50)
    check(f"18kg/90mg-kg-d/BID/50: mg={mg} ml={ml} (exp 810, 16.2)",
          abs(mg - 810.0) < 0.01 and abs(ml - 16.2) < 0.01)
    check("weight=0 raises",          raises(calc_peds_dose, 0, 90, 2, 50))
    check("fractional doses/day raises", raises(calc_peds_dose, 18, 90, 2.5, 50))

    section("calc_insulin_logic")
    check("10u/d, 10mL, 100u/mL = 100d",
          calc_insulin_logic(10, 10, 100) == 100)
    check("with priming 10u/d: 50d",
          calc_insulin_logic(10, 10, 100, priming_units_per_day=10) == 50)
    check("daily=0 raises",          raises(calc_insulin_logic, 0, 10, 100))
    check("3650-day cap raises",      raises(calc_insulin_logic, 0.001, 1000, 1000))

    section("verify_dea_logic")
    check("AB1234563 valid",          verify_dea_logic("AB1234563") is True)
    check("AB1234560 invalid checksum", verify_dea_logic("AB1234560") is False)
    check("lowercase accepted",        verify_dea_logic("ab1234563") is True)
    check("length 8 rejected",         verify_dea_logic("AB123456") is False)
    check("None rejected",             verify_dea_logic(None) is False)
    check("unicode rejected",          verify_dea_logic("ÄB1234563") is False)

    section("dea_registrant_type")
    _, p = dea_registrant_type("AB1234563")
    check("A-prefix is prescriber", p is True)
    _, p2 = dea_registrant_type("FB1234563")
    check("F-prefix is not prescriber", p2 is False)
    _, p3 = dea_registrant_type("XY1234563")
    check("X-prefix is prescriber", p3 is True)

    section("is_strong_pin")
    check("4729 accepted",            is_strong_pin("4729")[0] is True)
    check("1111 rejected (repeated)", is_strong_pin("1111")[0] is False)
    check("1234 rejected (asc)",      is_strong_pin("1234")[0] is False)
    check("4321 rejected (desc)",     is_strong_pin("4321")[0] is False)
    check("reuse rejected",           is_strong_pin("4729", old_pin="4729")[0] is False)
    check("length-3 rejected",        is_strong_pin("123")[0] is False)
    check("aaaa rejected (alpha rep)", is_strong_pin("aaaa")[0] is False)
    check("ab12 accepted (alpha-num)", is_strong_pin("ab12")[0] is True)
    check("None rejected",            is_strong_pin(None)[0] is False)

    section("normalize_answer / answer_matches")
    check("None → empty string",      normalize_answer(None) == "")
    check("dash+slash → spaces",
          normalize_answer("Hydro-Chloro/Thiazide") == "hydro chloro thiazide")
    check("extra whitespace collapsed", normalize_answer("  drug  name  ") == "drug name")
    check("case insensitive match",    answer_matches("ATORVASTATIN", "atorvastatin") is True)
    check("alias match (hctz)",        answer_matches("hctz", "Hydrochlorothiazide/HCTZ") is True)
    check("None user → False",         answer_matches(None, "Drug") is False)
    check("empty user → False",        answer_matches("", "Drug") is False)

    section("sm2_update")
    ease, iv, reps = sm2_update(None, None, None, True)
    check(f"First review: ease={ease} iv={iv} reps={reps} (exp 2.6, 1, 1)",
          (ease, iv, reps) == (2.6, 1, 1))

    ease2, iv2, reps2 = sm2_update(2.5, 30, 5, False)
    check(f"Incorrect reset: iv={iv2} reps={reps2} (exp 0, 0)",
          iv2 == 0 and reps2 == 0)

    # convergence: 20 correct cycles from None
    e, i, r = None, None, None
    for _ in range(20):
        e, i, r = sm2_update(e, i, r, True)
    check(f"20 correct cycles → interval={i} (expected >100)", i > 100)

    # ease floor never below 1.3
    ef = 1.3
    for _ in range(100):
        ef, _, _ = sm2_update(ef, 10, 3, False)
    check(f"Ease floor after 100 failures: {ef} (expected 1.3)", ef == 1.3)

    # monotone ease on correct
    ef, iv, r = 2.5, 0, 0
    prev = ef
    for _ in range(20):
        ef, iv, r = sm2_update(ef, iv, r, True)
        ok = ef >= prev
        prev = ef
    check("Ease never decreases on consecutive correct", ok)

    # ease finite after 1000 correct
    ef, iv, r = 2.5, 0, 0
    for _ in range(1000):
        ef, iv, r = sm2_update(ef, iv, r, True)
    check(f"Ease finite after 1000 correct: {ef:.1f} (expected <=105)",
          math.isfinite(ef) and ef <= 105.0)

    # NaN input
    ef2, iv2, r2 = sm2_update(float("nan"), 10, 3, True)
    check("NaN ease falls back to first-review defaults",
          math.isfinite(ef2) and iv2 == 1)


# ---------------------------------------------------------------------------
# Section 2 — Data layer (requires temp DB)
# ---------------------------------------------------------------------------

def _test_data(tmp_dir):
    from datetime import datetime, timedelta
    import pharmacy_app.data as D
    from pharmacy_app.logic import calculate_weight

    old_db = D.DB_FILE
    D.DB_FILE = os.path.join(tmp_dir, "debug_test.db")
    os.environ["HOME"] = tmp_dir

    try:
        D.init_db()

        section("Data: init + users")
        admins, techs = D.db_list_users()
        check("Admin Nathan seeded",       "Nathan" in admins)
        check("No techs on fresh init",    techs == [])
        D.init_db()  # idempotency
        check("Init is idempotent",        D.db_list_users()[0] == ["Nathan"])
        check("Add tech Alice",            D.db_add_user("Alice", "tech", "4729") is True)
        check("Alice in tech list",        "Alice" in D.db_list_users()[1])
        check("Blank name rejected",       D.db_add_user("   ", "tech") is False)
        check("Reserved name rejected",    D.db_add_user("admin", "tech") is False)
        check("Remove only admin refused", D.db_remove_user("Nathan") is False)
        D.db_add_user("SecondAdmin", "admin", "7410")
        check("Remove Nathan when 2nd admin exists", D.db_remove_user("Nathan") is True)

        section("Data: PIN verify")
        D.db_add_user("Carol", "tech", "9182")
        check("Correct PIN accepted",  D.db_verify_pin("Carol", "9182") is True)
        check("Wrong PIN rejected",    D.db_verify_pin("Carol", "0000") is False)
        check("None PIN rejected",     D.db_verify_pin("Carol", None) is False)
        check("Unknown user → False",  D.db_verify_pin("Ghost", "1234") is False)

        section("Data: audit log")
        D.db_log_audit("Alice", "action-1")
        D.db_log_audit("Alice", "action-2")
        rows = D.db_audit_log()
        check("2 audit rows",          len(rows) == 2)
        check("Newest first",          rows[0][2] == "action-2")
        check("Filter by text",        len(D.db_audit_log("action-1")) == 1)
        check("Limit respected",       len(D.db_audit_log(limit=1)) == 1)

        section("Data: inventory")
        D.db_add_inventory("Aspirin",   "2027-01-01")
        D.db_add_inventory("Ibuprofen", "2026-06-01")
        inv = D.db_inventory_list()
        check("2 inventory items",     len(inv) == 2)
        check("Filter by name",        D.db_inventory_list("asp") == [("Aspirin", "2027-01-01")])
        check("LIKE wildcard escaped", D.db_inventory_list("%") == [])
        exp = D.db_expired_inventory(today="2026-12-01")
        check("Ibuprofen expired by 2026-12-01",
              ("Ibuprofen", "2026-06-01") in exp)
        window = D.db_inventory_expiring(within_days=30, today="2026-05-20")
        check("Ibuprofen in 30-day expiry window",
              any(r[0] == "Ibuprofen" for r in window))
        D.db_remove_inventory("Aspirin")
        check("Remove inventory item", D.db_inventory_list("asp") == [])

        section("Data: partial fills")
        D.db_add_partial("Adderall", 30, "J. Doe",  "2026-05-20")
        D.db_add_partial("Xanax",    10, "R. Roe",  "2026-05-19")
        check("2 open partials",      D.db_open_partials_count() == 2)
        prows = D.db_open_partials()
        check("list_open has 2 rows", len(prows) == 2)
        pid = prows[0][0]
        check("Resolve returns True (first)",  D.db_resolve_partial(pid) is True)
        check("Resolve returns False (repeat)", D.db_resolve_partial(pid) is False)
        check("Open count now 1",     D.db_open_partials_count() == 1)
        check("Nonexistent id → False", D.db_resolve_partial(99999) is False)

        section("Data: mastery stats + calculate_weight")
        # Legacy path: all correct, no SRS timestamp
        D.db_upsert_mastery_stats("Alice", "Lipitor", 5, 5, 2.5, 1, 3, None)
        row = D.db_get_mastery_stats("Alice", "Lipitor")
        check("Upsert stores row", row is not None and row["total"] == 5)
        conn = D.get_db_connection()
        try:
            w = calculate_weight("Alice", "Lipitor", conn)
            check(f"Legacy all-correct weight = {w} (expected 1)", w == 1)
        finally:
            conn.close()

        # SRS overdue path
        long_ago = (datetime.now() - timedelta(days=40)).isoformat(timespec="seconds")
        D.db_upsert_mastery_stats("Alice", "Zoloft", 5, 5, 2.5, 1, 3, long_ago)
        conn = D.get_db_connection()
        try:
            w2 = calculate_weight("Alice", "Zoloft", conn)
            check(f"SRS overdue 40d weight = {w2} (expected 50 cap)", w2 == 50)
        finally:
            conn.close()

        # SRS not-yet-due path
        just_now = datetime.now().isoformat(timespec="seconds")
        D.db_upsert_mastery_stats("Alice", "Nexium", 5, 5, 2.5, 3, 2, just_now)
        conn = D.get_db_connection()
        try:
            w3 = calculate_weight("Alice", "Nexium", conn)
            check(f"SRS not-due (interval=3, days=0) weight = {w3} (expected 7)", w3 == 7)
        finally:
            conn.close()

        section("Data: backup + restore")
        path = D.db_backup()
        check("Backup file created", os.path.exists(path))
        backups = D.db_list_backups()
        check("db_list_backups finds backup", len(backups) >= 1)
        D.db_add_user("Temp", "tech", "9999")
        check("Temp added before restore", "Temp" in D.db_list_users()[1])
        D.db_restore(path)
        check("Temp gone after restore",   "Temp" not in D.db_list_users()[1])

        section("Data: score + performance")
        D.db_record_score("Alice", 8, 10)
        D.db_record_score("Alice", 6, 10)
        quizzes, pct = D.db_perf("Alice")
        check(f"{quizzes} quizzes at {pct}% (expected 2, 70)", quizzes == 2 and pct == 70)
        check("No scores → (0, 0)", D.db_perf("Nobody") == (0, 0))

        section("Data: state")
        D.db_set_state("debug_key", "debug_value")
        check("State roundtrip",  D.db_get_state("debug_key") == "debug_value")
        D.db_set_state("debug_key", "v2")
        check("State overwrite",  D.db_get_state("debug_key") == "v2")
        check("State default",    D.db_get_state("missing", "fallback") == "fallback")

    finally:
        D.DB_FILE = old_db


# ---------------------------------------------------------------------------
# Section 3 — Config constants
# ---------------------------------------------------------------------------

def _test_config():
    from pharmacy_app.config import (
        LOCKOUT_SECONDS,
        LOCKOUT_THRESHOLD,
        MAX_LOG_ENTRIES,
        RESERVED_TECH_NAMES,
        is_unverified,
    )
    section("Config constants")
    check(f"MAX_LOG_ENTRIES = {MAX_LOG_ENTRIES} (expected 10000)", MAX_LOG_ENTRIES == 10000)
    check(f"LOCKOUT_THRESHOLD = {LOCKOUT_THRESHOLD} (expected 3)",  LOCKOUT_THRESHOLD == 3)
    check(f"LOCKOUT_SECONDS = {LOCKOUT_SECONDS} (expected 300)",    LOCKOUT_SECONDS == 300)
    check("'admin' in RESERVED_TECH_NAMES",  "admin" in RESERVED_TECH_NAMES)
    check("is_unverified([]) = True",        is_unverified([]) is True)
    check("is_unverified(['brand_generic']) = True (all pending)",
          is_unverified(["brand_generic"]) is True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    global _VERBOSE
    p = argparse.ArgumentParser(description="Pharmacy App debug/diagnostic runner")
    p.add_argument("--verbose",  action="store_true", help="Show PASS lines and DEBUG log")
    p.add_argument("--no-data",  action="store_true", help="Skip data-layer (DB) tests")
    args = p.parse_args()
    _VERBOSE = args.verbose

    log_level = logging.DEBUG if args.verbose else logging.WARNING
    _setup_logging(level=log_level)

    print("Pharmacy App Debug Runner")
    print(f"Python {sys.version.split()[0]}  |  {sys.platform}")

    tmp_dir = tempfile.mkdtemp(prefix="pharma_debug_")
    try:
        run_safely("Logic tests",  _test_logic)
        if not args.no_data:
            run_safely("Data tests", lambda: _test_data(tmp_dir))
        run_safely("Config tests", _test_config)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"\n{'='*55}")
    total = _PASS + _FAIL
    print(f"  {_PASS}/{total} checks passed", end="")
    if _FAIL:
        print(f"  ({_FAIL} FAILED)")
        for e in _ERRORS:
            print(f"    • {e}")
    else:
        print("  — all green")
    print(f"{'='*55}")
    return 0 if _FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
