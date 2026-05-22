#!/usr/bin/env python3
"""Data-layer tests for pharmacy_app.data (pytest).

Covers the DB functions that previously had ZERO automated coverage.
Every test runs against a throwaway SQLite file in a pytest tmp_path,
so nothing touches the real pharmacy_master.db. HOME is also redirected
into tmp_path so backup/export functions write somewhere disposable.

Run:  pytest tests/test_data.py -q
"""

import os
import sys

import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pharmacy_app import data as D  # noqa: E402
from pharmacy_app.logic import calculate_weight  # noqa: E402


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Fresh, isolated DB per test. Patches data.DB_FILE to a temp
    file and HOME to tmp_path; runs init_db(); yields the data module."""
    monkeypatch.setattr(D, "DB_FILE", str(tmp_path / "test.db"))
    monkeypatch.setenv("HOME", str(tmp_path))
    D.init_db()
    return D


def _raw_insert(sql, params):
    """Insert a row directly — for tables (Inventory, PartialFills,
    PTCBMastery, MasteryStats) that have no dedicated data.py helper."""
    conn = D.get_db_connection()
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


# --- init_db --------------------------------------------------------
def test_init_db_seeds_one_admin(db):
    admins, techs = db.db_list_users()
    assert admins == ["Nathan"]
    assert techs == []


def test_init_db_is_idempotent(db):
    db.init_db()
    db.init_db()
    admins, _ = db.db_list_users()
    assert admins == ["Nathan"]          # still exactly one admin


def test_init_db_seeds_default_shift_notes(db):
    assert db.db_get_state("shift_notes") == "Welcome to your shift."


# --- db_add_user ----------------------------------------------------
def test_add_tech_then_listed(db):
    assert db.db_add_user("Alice", "tech", "4729") is True
    admins, techs = db.db_list_users()
    assert "Alice" in techs


def test_add_user_rejects_blank_name(db):
    assert db.db_add_user("   ", "tech") is False


def test_add_user_rejects_reserved_name(db):
    assert db.db_add_user("admin", "tech") is False
    assert db.db_add_user("System", "tech") is False   # case-insensitive


def test_add_user_rejects_role_collision(db):
    # A1 fix: cannot overwrite admin "Nathan" by re-adding as a tech.
    assert db.db_add_user("Nathan", "tech", "1111") is False
    admins, _ = db.db_list_users()
    assert "Nathan" in admins                          # still admin


# --- db_verify_pin --------------------------------------------------
def test_verify_pin_correct_and_wrong(db):
    db.db_add_user("Bob", "tech", "8675")
    assert db.db_verify_pin("Bob", "8675") is True
    assert db.db_verify_pin("Bob", "0000") is False


def test_verify_pin_none_and_unknown_user(db):
    assert db.db_verify_pin("Nathan", None) is False
    assert db.db_verify_pin("Ghost", "1234") is False


# --- db_remove_user -------------------------------------------------
def test_remove_tech_succeeds(db):
    db.db_add_user("Carol", "tech", "5391")
    assert db.db_remove_user("Carol") is True
    _, techs = db.db_list_users()
    assert "Carol" not in techs


def test_remove_last_admin_refused(db):
    # A3 fix: removing the only admin must be refused.
    assert db.db_remove_user("Nathan") is False
    admins, _ = db.db_list_users()
    assert "Nathan" in admins


def test_remove_admin_allowed_when_another_exists(db):
    db.db_add_user("SecondAdmin", "admin", "7410")
    assert db.db_remove_user("Nathan") is True


# --- db_get_state / db_set_state ------------------------------------
def test_state_roundtrip_and_default(db):
    assert db.db_get_state("missing", "fallback") == "fallback"
    db.db_set_state("missing", "now-set")
    assert db.db_get_state("missing") == "now-set"


def test_state_overwrite(db):
    db.db_set_state("k", "v1")
    db.db_set_state("k", "v2")
    assert db.db_get_state("k") == "v2"


# --- db_log_audit (incl. pruning) -----------------------------------
def test_audit_log_appends(db):
    db.db_log_audit("Nathan", "Logged In")
    conn = db.get_db_connection()
    try:
        n = conn.execute("SELECT COUNT(*) AS c FROM AuditLog").fetchone()["c"]
    finally:
        conn.close()
    assert n == 1


def test_audit_log_prunes_to_max(db, monkeypatch):
    monkeypatch.setattr(D, "MAX_LOG_ENTRIES", 3)
    for i in range(6):
        db.db_log_audit("Nathan", "action %d" % i)
    conn = db.get_db_connection()
    try:
        rows = conn.execute(
            "SELECT action FROM AuditLog ORDER BY id").fetchall()
    finally:
        conn.close()
    assert len(rows) == 3                              # pruned to cap
    assert rows[-1]["action"] == "action 5"            # newest kept


# --- db_record_score / db_perf / db_recent_scores -------------------
def test_perf_averages_scores(db):
    db.db_record_score("Alice", 8, 10)
    db.db_record_score("Alice", 6, 10)
    quizzes, pct = db.db_perf("Alice")
    assert quizzes == 2
    assert pct == 70                                   # (8+6)/(10+10)


def test_perf_empty_is_zero(db):
    assert db.db_perf("Nobody") == (0, 0)


def test_recent_scores_newest_first(db):
    db.db_record_score("Alice", 5, 10)
    db.db_record_score("Alice", 9, 10)
    recent = db.db_recent_scores("Alice", limit=10)
    assert recent[0][1] == 9                           # newest score first
    assert recent[0][3] == 90                          # pct computed


# --- db_expired_inventory -------------------------------------------
def test_expired_inventory_filters_by_date(db):
    _raw_insert("INSERT INTO Inventory VALUES (?, ?)", ("OldDrug", "2020-01-01"))
    _raw_insert("INSERT INTO Inventory VALUES (?, ?)", ("FreshDrug", "2099-01-01"))
    expired = db.db_expired_inventory(today="2026-05-20")
    assert expired == [("OldDrug", "2020-01-01")]


# --- db_open_partials_count -----------------------------------------
def test_open_partials_count(db):
    _raw_insert(
        "INSERT INTO PartialFills (drug, qty_owed, patient, date, resolved) "
        "VALUES (?, ?, ?, ?, ?)", ("DrugX", 5, "Pat", "2026-05-20", 0))
    _raw_insert(
        "INSERT INTO PartialFills (drug, qty_owed, patient, date, resolved) "
        "VALUES (?, ?, ?, ?, ?)", ("DrugY", 2, "Pat", "2026-05-20", 1))
    assert db.db_open_partials_count() == 1             # only unresolved


# --- db_mastered_brands ---------------------------------------------
def test_mastered_brands(db):
    _raw_insert("INSERT INTO PTCBMastery VALUES (?, ?)", ("Alice", "Lipitor"))
    result = db.db_mastered_brands("Alice", ["Lipitor", "Zoloft"])
    assert result == {"Lipitor"}


def test_mastered_brands_empty_input(db):
    assert db.db_mastered_brands("Alice", []) == set()


# --- db_weak_spots --------------------------------------------------
def test_weak_spots_ranks_misses(db):
    _raw_insert("INSERT INTO MasteryStats "
                "(tech_name, drug_name, correct, total) VALUES (?, ?, ?, ?)",
                ("Alice", "DrugA", 2, 10))             # missed 8
    _raw_insert("INSERT INTO MasteryStats "
                "(tech_name, drug_name, correct, total) VALUES (?, ?, ?, ?)",
                ("Alice", "DrugB", 9, 10))             # missed 1
    weak = db.db_weak_spots("Alice")
    assert weak[0][0] == "DrugA"                       # most-missed first
    assert weak[0][1] == 8


# --- ptcb_readiness -------------------------------------------------
def test_ptcb_readiness(db):
    _raw_insert("INSERT INTO PTCBMastery VALUES (?, ?)", ("Alice", "Lipitor"))
    mastered, total, pct = db.ptcb_readiness("Alice")
    assert mastered == 1
    assert total > 0
    assert 0 <= pct <= 100


# --- pure helpers ---------------------------------------------------
def test_like_escape():
    assert D._like_escape("a%b_c") == "a\\%b\\_c"
    assert D._like_escape("back\\slash") == "back\\\\slash"
    assert D._like_escape("") == ""


def test_date_is_valid():
    assert D._date_is_valid("2026-05-20") is True
    assert D._date_is_valid("2026-13-99") is False
    assert D._date_is_valid("not-a-date") is False


# --- backup / restore / list_backups --------------------------------
def test_backup_creates_file(db):
    path = db.db_backup()
    assert os.path.exists(path)


def test_list_backups_finds_backup(db):
    db.db_backup()
    backups = db.db_list_backups()
    assert len(backups) >= 1
    assert backups[0][0].startswith("pharmacy_backup_")


def test_restore_roundtrip(db):
    # snapshot -> add a user -> restore -> the added user is gone
    backup_path = db.db_backup()
    db.db_add_user("Temp", "tech", "9999")
    assert "Temp" in db.db_list_users()[1]
    db.db_restore(backup_path)
    assert "Temp" not in db.db_list_users()[1]


# --- exports --------------------------------------------------------
def test_export_inventory_writes_file(db):
    _raw_insert("INSERT INTO Inventory VALUES (?, ?)", ("DrugZ", "2030-01-01"))
    path = db.db_export_inventory()
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as fh:
        body = fh.read()
    assert "DrugZ" in body


def test_export_audit_log_writes_file(db):
    db.db_log_audit("Nathan", "Exported")
    path = db.db_export_audit_log()
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as fh:
        body = fh.read()
    assert "Exported" in body


# --- calculate_weight (logic.py, but DB-dependent) ------------------
def test_calculate_weight_no_stats_returns_base(db):
    conn = db.get_db_connection()
    try:
        assert calculate_weight("Alice", "Lipitor", conn) == 10
    finally:
        conn.close()


def test_calculate_weight_scales_with_misses(db):
    # missed = total - correct = 10 - 4 = 6 -> weight = 10 + 6*5 = 40
    _raw_insert("INSERT INTO MasteryStats "
                "(tech_name, drug_name, correct, total) VALUES (?, ?, ?, ?)",
                ("Alice", "Lipitor", 4, 10))
    conn = db.get_db_connection()
    try:
        assert calculate_weight("Alice", "Lipitor", conn) == 40
    finally:
        conn.close()


def test_calculate_weight_all_correct_returns_one(db):
    _raw_insert("INSERT INTO MasteryStats "
                "(tech_name, drug_name, correct, total) VALUES (?, ?, ?, ?)",
                ("Alice", "Zoloft", 10, 10))
    conn = db.get_db_connection()
    try:
        assert calculate_weight("Alice", "Zoloft", conn) == 1
    finally:
        conn.close()


def test_calculate_weight_single_miss_boundary(db):
    # missed == 1 boundary: 10 + 1*5 = 15 (kills the missed>0 -> >1 mutant)
    _raw_insert("INSERT INTO MasteryStats "
                "(tech_name, drug_name, correct, total) VALUES (?, ?, ?, ?)",
                ("Alice", "Mobic", 9, 10))
    conn = db.get_db_connection()
    try:
        assert calculate_weight("Alice", "Mobic", conn) == 15
    finally:
        conn.close()


def test_calculate_weight_handles_null_total(db):
    # a malformed row with NULL total must fall back to base weight 10,
    # not raise TypeError on the legacy missed = total - correct path
    _raw_insert("INSERT INTO MasteryStats "
                "(tech_name, drug_name, correct) VALUES (?, ?, ?)",
                ("Alice", "Lipitor", 5))
    conn = db.get_db_connection()
    try:
        assert calculate_weight("Alice", "Lipitor", conn) == 10
    finally:
        conn.close()


def test_calculate_weight_handles_null_correct(db):
    # a malformed row with NULL correct must also fall back to weight 10
    _raw_insert("INSERT INTO MasteryStats "
                "(tech_name, drug_name, total) VALUES (?, ?, ?)",
                ("Alice", "Zoloft", 8))
    conn = db.get_db_connection()
    try:
        assert calculate_weight("Alice", "Zoloft", conn) == 10
    finally:
        conn.close()


# --- MasteryStats SRS columns + migration ---------------------------
def _mastery_columns():
    conn = D.get_db_connection()
    try:
        rows = conn.execute("PRAGMA table_info(MasteryStats)").fetchall()
    finally:
        conn.close()
    return {r["name"] for r in rows}


def test_fresh_db_has_srs_columns(db):
    cols = _mastery_columns()
    for c in ("ease_factor", "interval_days", "last_reviewed",
              "repetitions"):
        assert c in cols


def test_init_db_migrates_pre_srs_mastery_table(tmp_path, monkeypatch):
    # a DB created under the OLD 4-column MasteryStats schema must gain
    # the SRS columns when init_db() runs, without losing existing rows
    monkeypatch.setattr(D, "DB_FILE", str(tmp_path / "legacy.db"))
    monkeypatch.setenv("HOME", str(tmp_path))
    conn = D.get_db_connection()
    try:
        conn.execute(
            "CREATE TABLE MasteryStats (tech_name TEXT, drug_name TEXT, "
            "correct INTEGER, total INTEGER, "
            "PRIMARY KEY (tech_name, drug_name))")
        conn.execute("INSERT INTO MasteryStats "
                     "(tech_name, drug_name, correct, total) "
                     "VALUES ('Alice', 'Lipitor', 3, 5)")
        conn.commit()
    finally:
        conn.close()
    D.init_db()                                    # runs the ALTER pass
    cols = _mastery_columns()
    assert {"ease_factor", "interval_days", "last_reviewed",
            "repetitions"} <= cols
    conn = D.get_db_connection()
    try:
        row = conn.execute(
            "SELECT correct, total, ease_factor FROM MasteryStats "
            "WHERE drug_name='Lipitor'").fetchone()
    finally:
        conn.close()
    assert row["correct"] == 3 and row["total"] == 5  # old data intact
    assert row["ease_factor"] is None                 # new col defaults NULL
    D.init_db()                                    # second run is a no-op


def test_calculate_weight_srs_overdue_outranks_due(db):
    from datetime import datetime, timedelta
    long_ago = (datetime.now() - timedelta(days=40)).isoformat(
        timespec="seconds")
    just_now = datetime.now().isoformat(timespec="seconds")
    # overdue card: reviewed 40d ago, interval only 1 day
    _raw_insert(
        "INSERT INTO MasteryStats (tech_name, drug_name, correct, total, "
        "ease_factor, interval_days, last_reviewed, repetitions) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("Alice", "Lipitor", 5, 5, 2.5, 1, long_ago, 3))
    # not-yet-due card: reviewed just now, interval 30 days
    _raw_insert(
        "INSERT INTO MasteryStats (tech_name, drug_name, correct, total, "
        "ease_factor, interval_days, last_reviewed, repetitions) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("Alice", "Zoloft", 5, 5, 2.5, 30, just_now, 3))
    conn = db.get_db_connection()
    try:
        overdue = calculate_weight("Alice", "Lipitor", conn)
        not_due = calculate_weight("Alice", "Zoloft", conn)
    finally:
        conn.close()
    assert overdue == 50            # min(50, 10 + 39*2) -> capped at 50
    assert not_due == max(1, 10 - 30)  # deep not-due -> floored at 1
    assert overdue > not_due


# --- panel read helpers (finding M1) --------------------------------
def test_db_inventory_expiring_window(db):
    _raw_insert("INSERT INTO Inventory VALUES (?, ?)",
                ("Aspirin", "2026-06-01"))      # within 30d of 2026-05-21
    _raw_insert("INSERT INTO Inventory VALUES (?, ?)",
                ("Lipitor", "2027-01-01"))      # far future
    rows = db.db_inventory_expiring(within_days=30, today="2026-05-21")
    assert rows == [("Aspirin", "2026-06-01")]


def test_db_inventory_expiring_includes_already_expired(db):
    _raw_insert("INSERT INTO Inventory VALUES (?, ?)",
                ("Old", "2020-01-01"))
    rows = db.db_inventory_expiring(within_days=30, today="2026-05-21")
    assert ("Old", "2020-01-01") in rows


def test_db_inventory_list_all_and_filtered(db):
    _raw_insert("INSERT INTO Inventory VALUES (?, ?)",
                ("Amoxicillin", "2026-09-01"))
    _raw_insert("INSERT INTO Inventory VALUES (?, ?)",
                ("Lisinopril", "2026-08-01"))
    assert len(db.db_inventory_list()) == 2
    assert db.db_inventory_list("amox") == [("Amoxicillin", "2026-09-01")]
    assert db.db_inventory_list("zzz") == []


def test_db_inventory_list_escapes_like_wildcards(db):
    _raw_insert("INSERT INTO Inventory VALUES (?, ?)",
                ("Drug100", "2026-08-01"))
    # a literal '%' must not behave as a wildcard
    assert db.db_inventory_list("%") == []


def test_db_audit_log_filter_and_limit(db):
    db.db_log_audit("Alice", "Logged In")
    db.db_log_audit("Bob", "Removed tech: Carol")
    full = db.db_audit_log()
    assert len(full) == 2
    assert full[0][1] == "Bob"                  # newest first
    assert len(db.db_audit_log(limit=1)) == 1
    hits = db.db_audit_log("Carol")             # matches action text
    assert len(hits) == 1 and hits[0][1] == "Bob"


def test_db_open_partials(db):
    _raw_insert(
        "INSERT INTO PartialFills (drug, qty_owed, patient, date) "
        "VALUES (?, ?, ?, ?)", ("Adderall", 30, "J. Doe", "2026-05-20"))
    _raw_insert(
        "INSERT INTO PartialFills (drug, qty_owed, patient, date, resolved) "
        "VALUES (?, ?, ?, ?, 1)", ("Xanax", 10, "R. Roe", "2026-05-19"))
    rows = db.db_open_partials()
    assert len(rows) == 1                       # resolved row excluded
    assert rows[0][1:] == ("Adderall", 30, "J. Doe", "2026-05-20")


def test_db_user_has_pin(db):
    db.db_add_user("Pinned", "tech", "9182")
    db.db_add_user("NoPin", "tech")
    assert db.db_user_has_pin("Pinned") is True
    assert db.db_user_has_pin("NoPin") is False
    assert db.db_user_has_pin("Ghost") is False   # nonexistent user


# --- panel write helpers (finding M1) -------------------------------
def test_db_mark_mastered_idempotent(db):
    db.db_mark_mastered("Alice", "Lipitor")
    db.db_mark_mastered("Alice", "Lipitor")        # INSERT OR IGNORE
    assert db.db_mastered_brands("Alice", ["Lipitor"]) == {"Lipitor"}


def test_db_get_mastery_stats_none_when_absent(db):
    assert db.db_get_mastery_stats("Alice", "Lipitor") is None


def test_db_upsert_mastery_stats_insert_then_replace(db):
    db.db_upsert_mastery_stats("Alice", "Lipitor", 1, 1, 2.5, 1,
                               1, "2026-05-20T10:00:00")
    row = db.db_get_mastery_stats("Alice", "Lipitor")
    assert (row["total"], row["correct"]) == (1, 1)
    # same (tech, drug) key -> replaced in place, not duplicated
    db.db_upsert_mastery_stats("Alice", "Lipitor", 3, 2, 2.6, 6,
                               2, "2026-05-21T10:00:00")
    row = db.db_get_mastery_stats("Alice", "Lipitor")
    assert (row["total"], row["correct"], row["repetitions"]) == (3, 2, 2)


def test_db_add_and_remove_inventory(db):
    db.db_add_inventory("Aspirin", "2027-01-01")
    assert db.db_inventory_list() == [("Aspirin", "2027-01-01")]
    db.db_add_inventory("Aspirin", "2028-06-30")   # OR REPLACE on PK
    assert db.db_inventory_list() == [("Aspirin", "2028-06-30")]
    db.db_remove_inventory("Aspirin")
    assert db.db_inventory_list() == []


def test_db_add_partial_appears_open(db):
    db.db_add_partial("Adderall", 30, "J. Doe", "2026-05-20")
    rows = db.db_open_partials()
    assert len(rows) == 1
    assert rows[0][1:] == ("Adderall", 30, "J. Doe", "2026-05-20")


def test_db_resolve_partial_reports_change(db):
    db.db_add_partial("Xanax", 10, "R. Roe", "2026-05-20")
    pid = db.db_open_partials()[0][0]
    assert db.db_resolve_partial(pid) is True      # first call changes a row
    assert db.db_resolve_partial(pid) is False     # already resolved
    assert db.db_open_partials() == []
