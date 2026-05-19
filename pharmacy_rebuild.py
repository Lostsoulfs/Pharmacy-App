#!/usr/bin/env python3
"""
Pharmacy Training & Workflow OS — Rebuild (Pydroid 3 / Tkinter target)

Build status: T1..T6 COMPLETE. Runnable end-to-end in Pydroid 3.
- S1 constants / clinical data
- S2 pure logic core (audited + EARS corrections)
- S3 data layer (fresh DB, 8 tables, parameterized writes)
- S4 UI (login, shell, all panels: home, quiz, tools, calculators,
  law, admin, tpr, hotkeys, partials, vaccines, sig, lookup)
- S5 entrypoint

Spec refs: constitution C-RULEs; EARS ears-behavior doc; ADR log.
Fresh DB, no migration (ADR-C01 REJECTED). Tkinter on Pydroid 3
(ADR-001). expanduser("~") verified app-private on-device (ADR-002).
"""

import os
import hashlib
import random
import difflib
from datetime import datetime, timedelta

# tkinter / sqlite3 imported in their own sections (T2/T3) so the
# logic core (S2) stays headlessly testable in isolation.

# ============================================================
# S1 — SYSTEM CONSTANTS & CONFIGURATION
# ============================================================
MAX_LOG_ENTRIES = 500
LOCKOUT_THRESHOLD = 3
LOCKOUT_SECONDS = 300
PRUNE_EVERY = 50
RESERVED_TECH_NAMES = {'admin', 'global', 'system', 'pharmacist'}

# Fresh DB; legacy filename retired with the migration subsystem
# (ADR-C01). Path verified app-private on S23 Ultra / Pydroid 3
# (ADR-002): expanduser("~") -> /data/user/0/ru.iiec.pydroid3/app_HOME
DB_FILE = os.path.join(os.path.expanduser("~"), "pharmacy_master.db")

# UNVERIFIED clinical/law data carried as-is per ADR-C05; the UI layer
# (T4/T5) MUST render this flag visibly next to any clinical/law entry.
CLINICAL_DATA_UNVERIFIED = True

# ---- Clinical reference data — carried verbatim from v13 per ADR-C05 ----
# NOT externally verified. UI MUST show UNVERIFIED warning on every panel
# that renders any entry from these structures.

RED_FLAGS = [
    {"q": "Patient picking up Warfarin and Advil (Ibuprofen)?",
     "a": "Bleeding Risk",
     "rationale": "NSAIDs increase blood-thinning effects."},
    {"q": "C-II Codeine syrup from out-of-state dentist?",
     "a": "Diversion Risk",
     "rationale": "Common red flag for forged scripts."},
    {"q": "Cash price for 90-day supply of Oxycodone?",
     "a": "Pharmacist Review",
     "rationale": "High volume C-II cash payments require pharmacist override."},
]

LASA_PAIRS = [
    {"q": "Look-Alike: Hydroxyzine vs Hydralazine. Which is for Itching?",
     "a": "Hydroxyzine",
     "rationale": "Hydralazine is for blood pressure."},
    {"q": "Sound-Alike: Humalog vs Humulin. Which is rapid-acting?",
     "a": "Humalog",
     "rationale": "Humulin is intermediate-acting."},
    {"q": "Look-Alike: Zyrtec vs Zyprexa. Which is for allergies?",
     "a": "Zyrtec",
     "rationale": "Zyprexa is an antipsychotic."},
]

SIG_ABBREVIATIONS = {
    "QD": "once daily", "QDAY": "once daily",
    "BID": "twice daily", "TID": "three times daily",
    "QID": "four times daily", "QHS": "at bedtime",
    "QAM": "every morning", "QPM": "every evening",
    "PRN": "as needed", "PO": "by mouth",
    "SL": "under the tongue", "TOP": "apply topically",
    "OU": "both eyes", "OD": "right eye", "OS": "left eye",
    "AU": "both ears", "AD": "right ear", "AS": "left ear",
    "AC": "before meals", "PC": "after meals",
    "Q4H": "every 4 hours", "Q6H": "every 6 hours",
    "Q8H": "every 8 hours", "Q12H": "every 12 hours",
    "UD": "as directed", "AAA": "apply to affected area",
    "NTE": "not to exceed",
}

COMMON_RX_FLAGS = [
    ("warfarin",       "NSAID / aspirin / antibiotic interactions: pharmacist review."),
    ("methotrexate",   "Weekly dosing risk. Verify not accidentally entered daily."),
    ("insulin",        "Confirm type, concentration, max daily dose, and days supply."),
    ("levothyroxine",  "Separate from calcium/iron; consistency matters."),
    ("tramadol",       "Controlled-substance workflow; serotonin/seizure-risk screen."),
    ("alprazolam",     "Controlled-substance workflow; sedation/duplicate benzo screen."),
    ("amoxicillin",    "Confirm allergy history and pediatric weight-based dosing when applicable."),
]

BRAND_GENERIC = [
    {"brand": "Lipitor",    "generic": "Atorvastatin"},
    {"brand": "Synthroid",  "generic": "Levothyroxine"},
    {"brand": "Prinivil",   "generic": "Lisinopril"},
    {"brand": "Glucophage", "generic": "Metformin"},
    {"brand": "Zocor",      "generic": "Simvastatin"},
    {"brand": "Cozaar",     "generic": "Losartan"},
    {"brand": "Prilosec",   "generic": "Omeprazole"},
    {"brand": "Neurontin",  "generic": "Gabapentin"},
    {"brand": "Norvasc",    "generic": "Amlodipine"},
    {"brand": "Vicodin",    "generic": "Hydrocodone/APAP"},
    {"brand": "Zoloft",     "generic": "Sertraline"},
    {"brand": "ProAir",     "generic": "Albuterol"},
    {"brand": "Flonase",    "generic": "Fluticasone"},
    {"brand": "Singulair",  "generic": "Montelukast"},
    {"brand": "Amoxil",     "generic": "Amoxicillin"},
    {"brand": "Mobic",      "generic": "Meloxicam"},
    {"brand": "Plavix",     "generic": "Clopidogrel"},
    {"brand": "Lexapro",    "generic": "Escitalopram"},
    {"brand": "Crestor",    "generic": "Rosuvastatin"},
    {"brand": "Advil",      "generic": "Ibuprofen"},
    {"brand": "Tylenol",    "generic": "Acetaminophen"},
    {"brand": "Lasix",      "generic": "Furosemide"},
    {"brand": "Desyrel",    "generic": "Trazodone"},
    {"brand": "Cymbalta",   "generic": "Duloxetine"},
    {"brand": "Klor-Con",   "generic": "Potassium Chloride"},
    {"brand": "Toprol XL",  "generic": "Metoprolol Succinate"},
    {"brand": "Lopressor",  "generic": "Metoprolol Tartrate"},
    {"brand": "Zantac",     "generic": "Ranitidine"},
    {"brand": "Pravachol",  "generic": "Pravastatin"},
    {"brand": "Coreg",      "generic": "Carvedilol"},
    {"brand": "Ultram",     "generic": "Tramadol"},
    {"brand": "Valium",     "generic": "Diazepam"},
    {"brand": "Xanax",      "generic": "Alprazolam"},
    {"brand": "Klonopin",   "generic": "Clonazepam"},
    {"brand": "Ativan",     "generic": "Lorazepam"},
    {"brand": "Coumadin",   "generic": "Warfarin"},
    {"brand": "Flomax",     "generic": "Tamsulosin"},
    {"brand": "Tenormin",   "generic": "Atenolol"},
    {"brand": "Effexor",    "generic": "Venlafaxine"},
    {"brand": "Seroquel",   "generic": "Quetiapine"},
    {"brand": "Risperdal",  "generic": "Risperidone"},
    {"brand": "Paxil",      "generic": "Paroxetine"},
    {"brand": "Prozac",     "generic": "Fluoxetine"},
    {"brand": "Wellbutrin", "generic": "Bupropion"},
    {"brand": "Adderall",   "generic": "Amphetamine/Dextroamphetamine"},
    {"brand": "Concerta",   "generic": "Methylphenidate"},
    {"brand": "Flexeril",   "generic": "Cyclobenzaprine"},
    {"brand": "Zanaflex",   "generic": "Tizanidine"},
]

BG = "#121212"
PANEL = "#1E1E1E"
TEXT = "#E0E0E0"
ACCENT = "#BB86FC"
DIM = "#757575"
GREEN = "#03DAC6"
RED = "#CF6679"

FONT_HEADING = ("Segoe UI", 16, "bold")
FONT_BODY = ("Segoe UI", 12)
FONT_BUTTON = ("Segoe UI", 10, "bold")

# ============================================================
# S2 — PURE LOGIC CORE  (audited v13 logic + EARS corrections)
# Headlessly testable. No tkinter/sqlite dependency.
# ============================================================

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
    priming_per_injection × injections_per_day.

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


def calculate_weight(tech_name, drug_name, conn):
    """C06-EARS: Quiz mastery weighting. Per-user, per-drug.
    Returns weight for random.choices(). Higher weight = higher probability
    of re-testing drugs the user has missed.
    
    Behavior (carried from v13 show_question/calculate_weight):
    - No prior stats: weight = 10 (base)
    - Prior stats: weight = 10 + (5 * missed_count)
    
    Consequence: drugs with prior misses are 5x more likely to appear,
    encouraging remediation. Hard mode uses this for adaptive difficulty.
    
    Note: DB is caller's responsibility; connection passed in for isolation.
    If query fails, returns base weight (10) and logs nothing (per v13).
    """
    try:
        stats = conn.execute(
            "SELECT correct, total FROM MasteryStats WHERE tech_name=? AND drug_name=?",
            (tech_name, drug_name)
        ).fetchone()
        if not stats or stats["total"] == 0:
            return 10
        missed = stats["total"] - stats["correct"]
        if missed > 0:
            return 10 + (missed * 5)
        return 1
    except Exception:
        return 10


# ============================================================
# S3 — DATA LAYER  (fresh DB, schema, CRUD; NO migration)
# T2 COMPLETE. No migrate_* functions. No LEGACY_JSON. Fresh DB.
# All writes parameterized. Headlessly tested.
# ============================================================
import sqlite3
from datetime import datetime, timedelta


def get_db_connection():
    """WAL, Row factory, busy timeout. Unchanged pattern from audited
    v13 (was sound)."""
    conn = sqlite3.connect(DB_FILE, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db():
    """Create schema if absent; seed one default admin if no admin
    exists. NO legacy gating (ADR-C01 — migration removed). Default
    admin PIN is the well-known '1234'; the UI MUST force a change on
    first admin login (carried behavior, T3)."""
    conn = get_db_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS Users (
                name TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                pin_hash TEXT
            );
            CREATE TABLE IF NOT EXISTS Scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tech_name TEXT NOT NULL,
                date TEXT NOT NULL,
                correct INTEGER NOT NULL,
                total INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Inventory (
                drug_name TEXT PRIMARY KEY,
                exp_date TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS AuditLog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user TEXT NOT NULL,
                action TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS AppState (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS PTCBMastery (
                tech_name TEXT,
                drug_name TEXT,
                PRIMARY KEY (tech_name, drug_name)
            );
            CREATE TABLE IF NOT EXISTS PartialFills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drug TEXT NOT NULL,
                qty_owed INTEGER NOT NULL,
                patient TEXT NOT NULL,
                date TEXT NOT NULL,
                resolved INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS MasteryStats (
                tech_name TEXT,
                drug_name TEXT,
                correct INTEGER,
                total INTEGER,
                PRIMARY KEY (tech_name, drug_name)
            );
            """
        )
        cur = conn.execute("SELECT COUNT(*) FROM Users WHERE role='admin'")
        if cur.fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO Users (name, role, pin_hash) VALUES (?, ?, ?)",
                ("Nathan", "admin", hash_pin("1234")),
            )
        conn.execute(
            "INSERT OR IGNORE INTO AppState (key, value) VALUES "
            "('shift_notes', 'Welcome to your shift.')"
        )
        conn.commit()
    finally:
        conn.close()


# ---- generic helpers (all parameterized) ----

def db_log_audit(user, action):
    """Append an audit row, then prune to MAX_LOG_ENTRIES newest."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO AuditLog (timestamp, user, action) VALUES (?, ?, ?)",
            (datetime.now().isoformat(timespec="seconds"), user, action),
        )
        conn.execute(
            "DELETE FROM AuditLog WHERE id NOT IN "
            "(SELECT id FROM AuditLog ORDER BY id DESC LIMIT ?)",
            (MAX_LOG_ENTRIES,),
        )
        conn.commit()
    finally:
        conn.close()


def db_add_user(name, role, pin=None):
    """Create/replace a user. Reserved names rejected. PIN hashed if
    given. Returns True on success, False if name reserved/blank."""
    if not name or not name.strip():
        return False
    if name.strip().lower() in RESERVED_TECH_NAMES:
        return False
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO Users (name, role, pin_hash) "
            "VALUES (?, ?, ?)",
            (name.strip(), role, hash_pin(pin) if pin else None),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def db_remove_user(name):
    """Cascading delete: user + their scores + mastery rows."""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM Users WHERE name=?", (name,))
        conn.execute("DELETE FROM Scores WHERE tech_name=?", (name,))
        conn.execute("DELETE FROM PTCBMastery WHERE tech_name=?", (name,))
        conn.execute("DELETE FROM MasteryStats WHERE tech_name=?", (name,))
        conn.commit()
    finally:
        conn.close()


def db_verify_pin(name, pin):
    """True iff user exists and the hash matches. None pin -> False."""
    if pin is None:
        return False
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT pin_hash FROM Users WHERE name=?", (name,)
        ).fetchone()
        if row is None or row["pin_hash"] is None:
            return False
        return row["pin_hash"] == hash_pin(pin)
    finally:
        conn.close()


def db_list_users():
    """Return (admins, techs) name lists, admins first."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT name, role FROM Users ORDER BY role, name"
        ).fetchall()
        admins = [r["name"] for r in rows if r["role"] == "admin"]
        techs = [r["name"] for r in rows if r["role"] != "admin"]
        return admins, techs
    finally:
        conn.close()


def db_get_state(key, default=None):
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT value FROM AppState WHERE key=?", (key,)
        ).fetchone()
        return row["value"] if row else default
    finally:
        conn.close()


def db_set_state(key, value):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO AppState (key, value) VALUES (?, ?)",
            (key, value),
        )
        conn.commit()
    finally:
        conn.close()


def db_record_score(tech, correct, total):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO Scores (tech_name, date, correct, total) "
            "VALUES (?, ?, ?, ?)",
            (tech, datetime.now().isoformat(timespec="seconds"),
             int(correct), int(total)),
        )
        conn.commit()
    finally:
        conn.close()


def db_perf(tech):
    """Return (quizzes_completed, avg_pct_int) for a tech."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT correct, total FROM Scores WHERE tech_name=?", (tech,)
        ).fetchall()
        if not rows:
            return 0, 0
        tot = sum(r["total"] for r in rows)
        cor = sum(r["correct"] for r in rows)
        pct = int((cor / tot) * 100) if tot else 0
        return len(rows), pct
    finally:
        conn.close()


def db_list_backups():
    """T7.14. Return list of (filename, abs_path, mtime) for files
    matching pharmacy_backup_*.db in the home dir, newest first."""
    home = os.path.expanduser("~")
    out = []
    try:
        for name in os.listdir(home):
            if (name.startswith("pharmacy_backup_")
                    and name.endswith(".db")):
                full = os.path.join(home, name)
                try:
                    mtime = os.path.getmtime(full)
                except OSError:
                    continue
                out.append((name, full, mtime))
    except OSError:
        return []
    out.sort(key=lambda x: x[2], reverse=True)
    return out


def db_restore(backup_path):
    """T7.14. Replace the live DB with the contents of backup_path
    via SQLite online backup API (in reverse direction). The current
    DB is fully overwritten. Caller MUST drop in-app references to
    any open handles and force the user to re-login.

    Raises sqlite3.Error / OSError on failure. On failure the live DB
    is left intact (online backup is transactional)."""
    src = sqlite3.connect(backup_path, timeout=15.0)
    try:
        dst = sqlite3.connect(DB_FILE, timeout=15.0)
        try:
            with dst:
                src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()


def db_open_partials_count():
    """T7.15. Count of PartialFills rows where resolved=0."""
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM PartialFills WHERE resolved=0"
        ).fetchone()
    finally:
        conn.close()
    return int(row["c"] or 0)


def db_expired_inventory(today=None):
    """T7.11. Return list of (drug_name, exp_date) for Inventory rows
    where exp_date < today (strictly past, NOT upcoming). today defaults
    to datetime.now() in ISO YYYY-MM-DD. Sorted oldest expiration
    first. Empty result -> []."""
    if today is None:
        today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT drug_name, exp_date FROM Inventory "
            "WHERE exp_date < ? ORDER BY exp_date ASC, drug_name ASC",
            (today,)
        ).fetchall()
    finally:
        conn.close()
    return [(r["drug_name"], r["exp_date"]) for r in rows]


def db_backup():
    """T7.10. Online SQLite backup via sqlite3.Connection.backup API.
    Safe with WAL and concurrent readers. Writes to a timestamped
    .db file next to the live DB. Returns absolute path written."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(
        os.path.expanduser("~"),
        "pharmacy_backup_%s.db" % stamp)
    src = sqlite3.connect(DB_FILE, timeout=15.0)
    try:
        dst = sqlite3.connect(path)
        try:
            with dst:
                src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()
    return path


def db_export_inventory():
    """T7.16. Export full Inventory table to a tab-separated plain
    text file next to the DB. Same format conventions as the audit
    export (header block + tsv rows). Returns absolute path written."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT drug_name, exp_date FROM Inventory "
            "ORDER BY exp_date ASC, drug_name ASC"
        ).fetchall()
    finally:
        conn.close()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(
        os.path.expanduser("~"),
        "pharmacy_inventory_export_%s.txt" % stamp)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("Pharmacy Inventory Export\n")
        fh.write("Generated: %s\n" % datetime.now().isoformat(
            timespec="seconds"))
        fh.write("Total items: %d\n" % len(rows))
        fh.write("Source DB: %s\n" % DB_FILE)
        fh.write("---\n")
        fh.write("drug_name\texp_date\n")
        for r in rows:
            fh.write("%s\t%s\n" % (r["drug_name"], r["exp_date"]))
    return path


def db_export_audit_log():
    """T7.9. Export the entire AuditLog (not just latest 50, not the
    UI filter view — full table) to a plain-text file next to the DB.
    Returns the absolute path written. Format: header block + one
    tab-separated row per entry, oldest first (chronological)."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT timestamp, user, action FROM AuditLog "
            "ORDER BY id ASC"
        ).fetchall()
    finally:
        conn.close()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(
        os.path.expanduser("~"),
        "pharmacy_audit_export_%s.txt" % stamp)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("Pharmacy Audit Log Export\n")
        fh.write("Generated: %s\n" % datetime.now().isoformat(
            timespec="seconds"))
        fh.write("Total entries: %d\n" % len(rows))
        fh.write("Source DB: %s\n" % DB_FILE)
        fh.write("---\n")
        fh.write("timestamp\tuser\taction\n")
        for r in rows:
            fh.write("%s\t%s\t%s\n" % (
                r["timestamp"], r["user"], r["action"]))
    return path


def db_mastered_brands(tech, brand_list):
    """T7.8. Return the subset of brand_list that this tech has
    mastered (per PTCBMastery). Empty input -> set(). Single
    parameterized query with dynamic IN placeholders."""
    if not brand_list:
        return set()
    placeholders = ",".join("?" * len(brand_list))
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT drug_name FROM PTCBMastery "
            "WHERE tech_name=? AND drug_name IN (" + placeholders + ")",
            (tech, *brand_list)
        ).fetchall()
    finally:
        conn.close()
    return {r["drug_name"] for r in rows}


def db_recent_scores(tech, limit=10):
    """T7.6. Return list of (date, correct, total, pct) for a tech's
    most recent quiz sessions, newest first, capped at `limit`."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT date, correct, total FROM Scores "
            "WHERE tech_name=? ORDER BY id DESC LIMIT ?",
            (tech, int(limit))
        ).fetchall()
    finally:
        conn.close()
    out = []
    for r in rows:
        total = r["total"] or 0
        correct = r["correct"] or 0
        pct = int((correct / total) * 100) if total > 0 else 0
        out.append((r["date"], correct, total, pct))
    return out


def db_weak_spots(tech, limit=5):
    """T7.5. Return list of (drug_name, missed, total, miss_pct) for
    the drugs this tech misses most, capped at `limit`. Sourced from
    MasteryStats. Rows with total=0 excluded (no data signal).
    Ordering: most-missed-count first, then highest miss-rate, then
    drug_name. Empty result -> []."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT drug_name, correct, total FROM MasteryStats "
            "WHERE tech_name=? AND total > 0",
            (tech,)
        ).fetchall()
    finally:
        conn.close()
    weak = []
    for r in rows:
        missed = r["total"] - r["correct"]
        if missed <= 0:
            continue
        miss_pct = int((missed / r["total"]) * 100)
        weak.append((r["drug_name"], missed, r["total"], miss_pct))
    weak.sort(key=lambda x: (-x[1], -x[3], x[0]))
    return weak[:limit]


def ptcb_readiness(tech):
    """T7.3. Return (mastered, total, pct_int) for a tech's PTCB
    readiness. mastered = COUNT(*) FROM PTCBMastery WHERE tech_name=?
    AND drug_name matches any brand in BRAND_GENERIC. total = len of
    BRAND_GENERIC. Empty pool -> (0, 0, 0) defensively."""
    total = len(BRAND_GENERIC)
    if total == 0:
        return 0, 0, 0
    pool = {d["brand"] for d in BRAND_GENERIC}
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT drug_name FROM PTCBMastery WHERE tech_name=?",
            (tech,)
        ).fetchall()
    finally:
        conn.close()
    mastered = sum(1 for r in rows if r["drug_name"] in pool)
    pct = int((mastered / total) * 100)
    return mastered, total, pct

# ============================================================
# S4 — UI LAYER  (Tkinter, Pydroid 3)
# T3 COMPLETE: shell, auth+lockout, nav, real Home/Tools.
# T4/T5: feature panels (currently labeled placeholders, not
# silent stubs). Clinical/law entries MUST show the UNVERIFIED
# tag when implemented (ADR-C05).
# Phone-oriented: vertical scroll, large touch targets.
# ============================================================
import time
import tkinter as tk
from tkinter import simpledialog, messagebox


class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.user = None
        self.is_admin = False
        # In-memory lockout (resets on app restart). Decision: bare-bones,
        # matches v13 behavior class; persistent lockout deferred (not in
        # scope). Constants from S1: LOCKOUT_THRESHOLD / LOCKOUT_SECONDS.
        self._admin_fails = 0
        self._admin_lock_until = 0.0
        # T7.7 — audit log filter persists across re-renders of
        # panel_admin. Empty string = no filter.
        self._audit_filter = ""
        # T7.12 — inventory drug-name filter, same persistence pattern.
        self._inv_filter = ""

        root.title("Pharmacy OS")
        try:
            root.geometry("420x860")  # Pydroid fullscreens; hint only
        except Exception:
            pass
        root.configure(bg=BG)
        self.container = tk.Frame(root, bg=BG)
        self.container.pack(fill="both", expand=True)

        init_db()
        self.login_screen()

    # ---- helpers ----
    def _clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def make_scrollable(self, parent):
        """Vertical scroll area; inner width synced to canvas so content
        fills a narrow phone screen."""
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        win = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(win, width=e.width),
        )
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        # Desktop wheel; on-device touch-drag is Scott's to verify.
        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )
        return inner

    # ---- auth ----
    def login_screen(self):
        self._clear()
        f = tk.Frame(self.container, bg=BG)
        f.pack(fill="both", expand=True)
        tk.Label(f, text="Pharmacy OS", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 26, "bold")).pack(pady=28)
        admins, techs = db_list_users()
        for a in admins:
            tk.Button(f, text="%s (Admin)" % a, font=FONT_BUTTON, bg=PANEL,
                      fg=TEXT, height=2, bd=0,
                      command=lambda n=a: self._admin_login(n)
                      ).pack(fill="x", padx=24, pady=8)
        tk.Label(f, text="--- Technicians ---", bg=BG, fg=DIM,
                 font=FONT_BODY).pack(pady=12)
        for t in techs:
            tk.Button(f, text=t, font=FONT_BUTTON, bg=PANEL, fg=TEXT,
                      height=2, bd=0,
                      command=lambda n=t: self._tech_login(n)
                      ).pack(fill="x", padx=24, pady=6)
        if not techs:
            tk.Label(f, text="(no technicians yet — add in Admin Control)",
                     bg=BG, fg=DIM, font=FONT_BODY).pack(pady=6)

    def _admin_login(self, name):
        now = time.time()
        if now < self._admin_lock_until:
            secs = int(self._admin_lock_until - now)
            messagebox.showerror(
                "Locked", "Admin access locked for %d seconds." % secs)
            return
        pin = simpledialog.askstring(
            "Admin", "Enter PIN:", show="*", parent=self.root)
        if pin is None:
            return
        if db_verify_pin(name, pin):
            self._admin_fails = 0
            if pin == "1234":
                self._force_pin_change(name)
            self._enter(name, admin=True)
        else:
            self._admin_fails += 1
            remaining = LOCKOUT_THRESHOLD - self._admin_fails
            if remaining <= 0:
                self._admin_lock_until = now + LOCKOUT_SECONDS
                self._admin_fails = 0
                messagebox.showerror(
                    "Locked",
                    "Admin access locked for %d seconds." % LOCKOUT_SECONDS)
            else:
                messagebox.showerror(
                    "Denied",
                    "Invalid PIN. %d attempt(s) before lockout." % remaining)

    def _force_pin_change(self, name):
        messagebox.showinfo(
            "Security", "Default PIN in use. Set a new admin PIN.")
        while True:
            new = simpledialog.askstring(
                "Set PIN", "New admin PIN (min 4 chars):",
                show="*", parent=self.root)
            if new is None:
                continue  # forced — cannot cancel out
            # old_pin='1234': forced change only triggers on default
            # login, so this also blocks reverting to the default.
            ok, reason = is_strong_pin(new, old_pin="1234")
            if ok:
                db_add_user(name, "admin", new)
                messagebox.showinfo("Security", "Admin PIN updated.")
                return
            messagebox.showerror("Invalid", reason)

    def _tech_login(self, name):
        self._enter(name, admin=False)

    def _enter(self, name, admin):
        self.user = name
        self.is_admin = admin
        db_log_audit(name, "Logged In")
        self._build_shell()
        self.navigate_to("home")
        # T7.11 + T7.15 — Login briefing. Combines expired-stock alert
        # with open-partials count into one popup so users get the
        # full shift-start picture in one place, not two popups.
        expired = db_expired_inventory()
        open_partials = db_open_partials_count()
        sections = []
        if expired:
            lines = ["%s  —  expired %s" % (d, e) for d, e in expired]
            shown = lines[:10]
            if len(lines) > len(shown):
                shown.append("...and %d more." % (len(lines) - len(shown)))
            sections.append(
                "EXPIRED STOCK — do not dispense:\n" + "\n".join(shown))
        if open_partials > 0:
            sections.append(
                "OPEN PARTIALS: %d unresolved on the ledger."
                % open_partials)
        if sections:
            messagebox.showwarning(
                "Shift Briefing",
                "\n\n".join(sections))

    def logout(self):
        if self.user:
            db_log_audit(self.user, "Logged Out")
        self.user = None
        self.is_admin = False
        self.login_screen()

    # ---- shell + routing ----
    def _build_shell(self):
        self._clear()
        self.shell = tk.Frame(self.container, bg=BG)
        self.shell.pack(fill="both", expand=True)
        top = tk.Frame(self.shell, bg=PANEL)
        top.pack(fill="x")
        tk.Label(top, text="User: %s" % self.user, bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(side="left", padx=8, pady=6)
        tk.Button(top, text="Logout", bg=RED, fg=BG, font=FONT_BUTTON,
                  bd=0, command=self.logout).pack(side="right", padx=8, pady=4)
        nav = tk.Frame(self.shell, bg=BG)
        nav.pack(fill="x")
        items = [("Home", "home"), ("Training", "quiz"),
                 ("Tools", "tools"), ("Calc", "calculators"),
                 ("Law", "law")]
        if self.is_admin:
            items.append(("Admin", "admin"))
        for label, route in items:
            tk.Button(nav, text=label, bg=PANEL, fg=TEXT, font=FONT_BUTTON,
                      bd=0, command=lambda r=route: self.navigate_to(r)
                      ).pack(side="left", expand=True, fill="x",
                             padx=2, pady=4)
        self.content_host = tk.Frame(self.shell, bg=BG)
        self.content_host.pack(fill="both", expand=True)

    def navigate_to(self, target):
        for w in self.content_host.winfo_children():
            w.destroy()
        routes = {
            "home": self.panel_home,
            "quiz": self.panel_quiz,
            "tools": self.panel_tools,
            "calculators": self.panel_calculators,
            "law": self.panel_law,
            "admin": self.panel_admin,
            "tpr": self.panel_tpr,
            "hotkeys": self.panel_hotkeys,
            "partials": self.panel_partials,
            "vaccines": self.panel_vaccines,
            "sig": self.panel_sig,
            "lookup": self.panel_lookup,
        }
        fn = routes.get(target)
        if fn:
            fn()

    # ---- panels ----
    def panel_home(self):
        host = self.make_scrollable(self.content_host)
        title = "Home Dashboard" if self.is_admin else "Station Dashboard"
        tk.Label(host, text=title, bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=14)

        # Shift Notes
        sn = tk.Frame(host, bg=PANEL)
        sn.pack(fill="x", padx=16, pady=8)
        tk.Label(sn, text="Shift Notes", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 2))
        tk.Label(sn, text=db_get_state("shift_notes",
                                       "Welcome to your shift."),
                 bg=PANEL, fg=TEXT, font=FONT_BODY, wraplength=340,
                 justify="left").pack(anchor="w", padx=10, pady=(0, 10))

        # T7.1 — Expiration alerts. Reads Inventory for exp_date within
        # the next 30 days (or already expired). ISO date strings sort
        # lexicographically, so SQLite string compare is correct here.
        today = datetime.now().strftime("%Y-%m-%d")
        soon = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        conn = get_db_connection()
        try:
            expiring = conn.execute(
                "SELECT drug_name, exp_date FROM Inventory "
                "WHERE exp_date <= ? ORDER BY exp_date ASC, drug_name ASC",
                (soon,)
            ).fetchall()
        finally:
            conn.close()

        ef = tk.Frame(host, bg=PANEL)
        ef.pack(fill="x", padx=16, pady=8)
        tk.Label(ef, text="Expiration Alerts (≤ 30 days)",
                 bg=PANEL, fg=ACCENT, font=FONT_BUTTON).pack(
                     anchor="w", padx=10, pady=(8, 2))
        if not expiring:
            tk.Label(ef, text="No upcoming expirations.",
                     bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                         anchor="w", padx=10, pady=(0, 10))
        else:
            for r in expiring:
                is_expired = r["exp_date"] <= today
                color = RED if is_expired else ACCENT
                tag = "EXPIRED" if is_expired else "expires"
                tk.Label(
                    ef,
                    text="%s  —  %s %s" % (
                        r["drug_name"], tag, r["exp_date"]),
                    bg=PANEL, fg=color, font=FONT_BODY,
                    anchor="w", wraplength=320, justify="left"
                ).pack(anchor="w", padx=14, pady=2)
            tk.Frame(ef, bg=PANEL, height=6).pack()

        # Tech performance card
        if not self.is_admin:
            q, avg = db_perf(self.user)
            pf = tk.Frame(host, bg=PANEL)
            pf.pack(fill="x", padx=16, pady=8)
            tk.Label(pf, text="My Performance", bg=PANEL, fg=ACCENT,
                     font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 2))
            tk.Label(pf, text="Quizzes Completed: %d" % q, bg=PANEL,
                     fg=TEXT, font=FONT_BODY).pack(anchor="w", padx=10)
            tk.Label(pf, text="Average Score: %d%%" % avg, bg=PANEL,
                     fg=TEXT, font=FONT_BODY).pack(anchor="w", padx=10,
                                                   pady=(0, 10))

            # T7.3 — PTCB readiness. Counts distinct mastered drugs
            # from PTCBMastery for this tech, against BRAND_GENERIC pool.
            mastered, total, pct = ptcb_readiness(self.user)
            rf = tk.Frame(host, bg=PANEL)
            rf.pack(fill="x", padx=16, pady=8)
            tk.Label(rf, text="PTCB Readiness", bg=PANEL, fg=ACCENT,
                     font=FONT_BUTTON).pack(anchor="w", padx=10,
                                            pady=(8, 2))
            tk.Label(rf,
                     text="Mastered: %d / %d  (%d%%)" % (
                         mastered, total, pct),
                     bg=PANEL, fg=GREEN if pct >= 80 else TEXT,
                     font=FONT_BODY).pack(anchor="w", padx=10)
            tk.Label(rf,
                     text=("Ready for exam." if pct >= 80
                           else "Keep drilling Top 200 quiz."),
                     bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                         anchor="w", padx=10, pady=(0, 10))

            # T7.5 — Weak Spots: top 5 drugs this tech misses most.
            weak = db_weak_spots(self.user, limit=5)
            wf = tk.Frame(host, bg=PANEL)
            wf.pack(fill="x", padx=16, pady=8)
            tk.Label(wf, text="Weak Spots — Drill These",
                     bg=PANEL, fg=ACCENT, font=FONT_BUTTON).pack(
                         anchor="w", padx=10, pady=(8, 4))
            if not weak:
                tk.Label(wf,
                         text="No miss data yet. Run a quiz to "
                              "see weak spots.",
                         bg=PANEL, fg=DIM, font=FONT_BODY,
                         wraplength=320, justify="left").pack(
                             anchor="w", padx=14, pady=(0, 10))
            else:
                for drug, missed, total, miss_pct in weak:
                    tk.Label(
                        wf,
                        text="%s  —  missed %d/%d  (%d%%)" % (
                            drug, missed, total, miss_pct),
                        bg=PANEL, fg=RED if miss_pct >= 50 else TEXT,
                        font=FONT_BODY, anchor="w",
                        wraplength=320, justify="left"
                    ).pack(anchor="w", padx=14, pady=2)
                tk.Frame(wf, bg=PANEL, height=6).pack()

            # T7.6 — Recent Quizzes: last 10 sessions, newest first.
            recent = db_recent_scores(self.user, limit=10)
            rqf = tk.Frame(host, bg=PANEL)
            rqf.pack(fill="x", padx=16, pady=8)
            tk.Label(rqf, text="Recent Quizzes",
                     bg=PANEL, fg=ACCENT, font=FONT_BUTTON).pack(
                         anchor="w", padx=10, pady=(8, 4))
            if not recent:
                tk.Label(rqf,
                         text="No quizzes recorded yet.",
                         bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                             anchor="w", padx=14, pady=(0, 10))
            else:
                for date, correct, total, pct in recent:
                    if pct >= 80:
                        col = GREEN
                    elif pct >= 50:
                        col = TEXT
                    else:
                        col = RED
                    tk.Label(
                        rqf,
                        text="%s  —  %d / %d  (%d%%)" % (
                            date, correct, total, pct),
                        bg=PANEL, fg=col, font=FONT_BODY,
                        anchor="w", wraplength=320, justify="left"
                    ).pack(anchor="w", padx=14, pady=1)
                tk.Frame(rqf, bg=PANEL, height=6).pack()

    def panel_tools(self):
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Clinical Tools", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=14)
        for label, route in [("SIG Decoder", "sig"),
                             ("Drug Lookup", "lookup"),
                             ("Vaccine Eligibility", "vaccines"),
                             ("Partial Fill Ledger", "partials"),
                             ("TPR Insurance Guide", "tpr"),
                             ("IC+ Hotkeys", "hotkeys")]:
            tk.Button(host, text=label, bg=PANEL, fg=TEXT, font=FONT_BUTTON,
                      height=2, bd=0,
                      command=lambda r=route: self.navigate_to(r)
                      ).pack(fill="x", padx=24, pady=6)

    # ---- T5.1: panel_quiz (Training Center) ----
    # C06-EARS: Carried from v13 methods panel_quiz_picker, launch_quiz,
    # show_question, check_answer. Per-user mastery tracking + adaptive
    # hard mode. Quiz modes: b2g (brand→generic), g2b (generic→brand),
    # hard (weighted by missed), redflag (clinical red flags), lasa
    # (look-alike/sound-alike). Session = 10 questions; score saved to DB.
    # All quiz data (RED_FLAGS, LASA_PAIRS, BRAND_GENERIC) marked
    # UNVERIFIED per ADR-C05; UI renders visible warning.
    
    def panel_quiz(self):
        """Mode selection for quiz. Routes to launch_quiz(mode)."""
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Training Center", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)
        tk.Label(host, text="⚠ UNVERIFIED DATA — v13 source, not externally validated.",
                 bg=BG, fg=RED, font=FONT_BODY, wraplength=360,
                 justify="left").pack(padx=14, pady=(0, 8))
        
        modes = [
            ("Top 200: Brand → Generic", "b2g"),
            ("Top 200: Generic → Brand", "g2b"),
            ("Smart Hard Mode (Focus Drugs)", "hard"),
            ("Red Flags & Scenarios", "redflag"),
            ("LASA (Look-Alike Sound-Alike)", "lasa")
        ]
        for label, mode_key in modes:
            tk.Button(host, text=label, font=FONT_BODY, bg=PANEL, fg=TEXT,
                      height=2, bd=0,
                      command=lambda m=mode_key: self.launch_quiz(m)
                      ).pack(fill="x", padx=14, pady=5)

    def launch_quiz(self, mode):
        """Initialize quiz state. Called by panel_quiz mode buttons."""
        self.quiz_mode = mode
        self.quiz_score = 0
        self.quiz_total = 0
        self.show_question()

    def show_question(self):
        """Render next quiz question. Clears content_host, draws question
        + entry field + submit button. Binds Return to check_answer."""
        for widget in self.content_host.winfo_children():
            widget.destroy()
        
        main_f = tk.Frame(self.content_host, bg=BG)
        main_f.pack(fill="both", expand=True, padx=14, pady=12)

        # Select question based on mode
        if self.quiz_mode == "redflag":
            self.current_q = random.choice(RED_FLAGS)
            q_text = self.current_q["q"]
            self.correct_ans = self.current_q["a"]
        elif self.quiz_mode == "lasa":
            self.current_q = random.choice(LASA_PAIRS)
            q_text = self.current_q["q"]
            self.correct_ans = self.current_q["a"]
        else:
            # Drug-based quiz modes (b2g, g2b, hard)
            drugs = BRAND_GENERIC
            if self.quiz_mode == "hard":
                conn = None
                try:
                    conn = get_db_connection()
                    weights = [
                        calculate_weight(self.user, d["brand"], conn)
                        for d in drugs
                    ]
                    self.current_drug = random.choices(drugs, weights=weights, k=1)[0]
                except Exception:
                    self.current_drug = random.choice(drugs)
                finally:
                    if conn:
                        conn.close()
            else:
                self.current_drug = random.choice(drugs)
            
            if self.quiz_mode == "b2g":
                q_text = "What is the GENERIC for: %s?" % self.current_drug["brand"]
                self.correct_ans = self.current_drug["generic"]
            else:  # g2b
                q_text = "What is the BRAND for: %s?" % self.current_drug["generic"]
                self.correct_ans = self.current_drug["brand"]

        # Render question
        tk.Label(main_f, text="Question %d" % (self.quiz_total + 1),
                 font=FONT_BODY, bg=BG, fg=DIM).pack(pady=(0, 12))
        tk.Label(main_f, text=q_text, font=FONT_HEADING, bg=BG, fg=TEXT,
                 wraplength=500, justify="center").pack(pady=20)
        
        # Entry field
        self.ans_entry = tk.Entry(main_f, font=FONT_HEADING, bg=PANEL,
                                   fg=TEXT, insertbackground=TEXT,
                                   justify="center")
        self.ans_entry.pack(pady=10, ipady=10, fill="x")
        self.ans_entry.focus()
        self.ans_entry.bind("<Return>", lambda e: self.check_answer())
        
        # Submit button
        tk.Button(main_f, text="Submit Answer", font=FONT_BUTTON,
                  bg=ACCENT, fg=BG, bd=0, command=self.check_answer
                  ).pack(pady=20, fill="x")

    def check_answer(self):
        """Validate answer, update mastery stats, save score after 10 Qs.
        Fuzzy matching for scenarios (80%+ similarity via difflib);
        exact matching for drugs (answer_matches). Feedback via messagebox."""
        user_val = self.ans_entry.get().strip().lower()
        self.quiz_total += 1
        is_scenario = self.quiz_mode in ["redflag", "lasa"]
        is_correct = False

        # Validate answer
        if is_scenario:
            similarity = difflib.SequenceMatcher(None, user_val,
                                                 self.correct_ans.lower()).ratio()
            is_correct = similarity >= 0.8
        else:
            is_correct = answer_matches(user_val, self.correct_ans)

        # Track mastery stats (drug modes only)
        if not is_scenario:
            drug_name = self.current_drug["brand"]
            conn = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                if is_correct:
                    cursor.execute(
                        "INSERT OR IGNORE INTO PTCBMastery (tech_name, drug_name) VALUES (?, ?)",
                        (self.user, drug_name)
                    )
                cursor.execute(
                    "SELECT total, correct FROM MasteryStats WHERE tech_name=? AND drug_name=?",
                    (self.user, drug_name)
                )
                row = cursor.fetchone()
                if row:
                    new_total = row["total"] + 1
                    new_correct = row["correct"] + (1 if is_correct else 0)
                    cursor.execute(
                        "UPDATE MasteryStats SET total=?, correct=? WHERE tech_name=? AND drug_name=?",
                        (new_total, new_correct, self.user, drug_name)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO MasteryStats (tech_name, drug_name, total, correct) VALUES (?, ?, 1, ?)",
                        (self.user, drug_name, 1 if is_correct else 0)
                    )
                conn.commit()
            except Exception:
                pass  # Silent fail; mastery tracking non-critical
            finally:
                if conn:
                    conn.close()

        # Feedback
        if is_correct:
            self.quiz_score += 1
            rat = self.current_q.get("rationale", "") if is_scenario else ""
            feedback = "Correct! %s" % self.correct_ans
            if rat:
                feedback += "\n%s" % rat
            messagebox.showinfo("Correct!", feedback)
        else:
            rat = self.current_q.get("rationale", "") if is_scenario else ""
            feedback = "Not quite. The answer was: %s" % self.correct_ans
            if rat:
                feedback += "\n%s" % rat
            messagebox.showerror("Incorrect", feedback)

        # End quiz or continue
        if self.quiz_total >= 10:
            conn = None
            try:
                conn = get_db_connection()
                date_str = datetime.now().strftime("%Y-%m-%d")
                conn.execute(
                    "INSERT INTO Scores (tech_name, date, correct, total) VALUES (?, ?, ?, ?)",
                    (self.user, date_str, self.quiz_score, 10)
                )
                conn.commit()
            except Exception:
                pass  # Silent fail; score save non-critical
            finally:
                if conn:
                    conn.close()
            self.navigate_to("home")
        else:
            self.show_question()

    def panel_calculators(self):
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Calculators", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)

        def section(title):
            f = tk.Frame(host, bg=PANEL)
            f.pack(fill="x", padx=14, pady=8)
            tk.Label(f, text=title, bg=PANEL, fg=ACCENT,
                     font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
            return f

        def field(parent, label):
            r = tk.Frame(parent, bg=PANEL)
            r.pack(fill="x", padx=10, pady=3)
            tk.Label(r, text=label, bg=PANEL, fg=TEXT, font=FONT_BODY,
                     width=16, anchor="w").pack(side="left")
            e = tk.Entry(r, font=FONT_BODY, bg=BG, fg=TEXT,
                         insertbackground=TEXT)
            e.pack(side="left", fill="x", expand=True, ipady=4)
            return e

        # --- Insulin days supply (calls calc_insulin_logic) ---
        ins = section("Insulin Days Supply")
        i_daily = field(ins, "Units/day")
        i_ml = field(ins, "Total mL")
        i_conc = field(ins, "Concentration")
        # T7.17 — F-06 fix. Priming units/day. Pens waste ~2u per
        # injection on priming; pharmacist enters
        # priming_per_injection * injections_per_day. Default 0 = vial.
        i_prime = field(ins, "Priming u/day")
        i_prime.insert(0, "0")
        i_res = tk.Label(ins, text="--", bg=PANEL, fg=DIM,
                         font=FONT_BUTTON)
        i_res.pack(pady=8)

        def run_insulin():
            try:
                days = calc_insulin_logic(
                    i_daily.get(), i_ml.get(), i_conc.get(),
                    i_prime.get() or "0")
                i_res.config(text="%d days supply" % days, fg=GREEN)
            except ValueError as e:
                i_res.config(text=str(e), fg=RED)

        tk.Button(ins, text="Calculate", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0, command=run_insulin
                  ).pack(fill="x", padx=10, pady=(0, 10))

        # --- Days supply (calls calc_days_supply_logic) ---
        ds = section("Days Supply")
        d_qty = field(ds, "Quantity")
        d_day = field(ds, "Units/day")
        d_res = tk.Label(ds, text="--", bg=PANEL, fg=DIM,
                         font=FONT_BUTTON)
        d_res.pack(pady=8)

        def run_days():
            try:
                days = calc_days_supply_logic(d_qty.get(), d_day.get())
                d_res.config(text="%d days supply" % days, fg=GREEN)
            except ValueError as e:
                d_res.config(text=str(e), fg=RED)

        tk.Button(ds, text="Calculate", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0, command=run_days
                  ).pack(fill="x", padx=10, pady=(0, 10))

        # --- DEA checksum (calls verify_dea_logic) ---
        dea = section("DEA Checksum")
        dea_e = field(dea, "DEA number")
        dea_res = tk.Label(dea, text="--", bg=PANEL, fg=DIM,
                           font=FONT_BUTTON)
        dea_res.pack(pady=8)

        def run_dea():
            raw = dea_e.get()
            checksum_ok = verify_dea_logic(raw)
            type_label, is_prescriber = dea_registrant_type(raw)
            if not checksum_ok:
                dea_res.config(text="INVALID / forgery flag", fg=RED)
                return
            # T7.20 — registrant-type flag. Non-prescriber prefix on a
            # dispensing prescription is itself a forgery signal.
            if type_label and not is_prescriber:
                dea_res.config(
                    text="Checksum OK — but %s — NOT a prescriber, "
                         "VERIFY before dispensing" % type_label,
                    fg=RED)
            elif type_label:
                dea_res.config(
                    text="VALID — %s" % type_label, fg=GREEN)
            else:
                dea_res.config(text="VALID checksum", fg=GREEN)

        tk.Button(dea, text="Verify", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0, command=run_dea
                  ).pack(fill="x", padx=10, pady=(0, 10))

    def panel_law(self):
        # T5.2 + T7.19 — panel_law. Verbatim v13 bullets, UNVERIFIED
        # banner per ADR-C05, plus citation to MS Board of Pharmacy
        # authoritative source (Nathan, pharmacist, 2026-05-19).
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Mississippi Pharmacy Law & Safety",
                 bg=BG, fg=TEXT, font=FONT_HEADING).pack(pady=12)
        tk.Label(host,
                 text=("⚠ UNVERIFIED — bullets carried from v13 "
                       "source. Not yet cross-checked against the "
                       "official text below."),
                 bg=BG, fg=RED, font=FONT_BODY, wraplength=360,
                 justify="left").pack(padx=14, pady=(0, 4))
        tk.Label(host,
                 text=("Source of truth: Mississippi Board of "
                       "Pharmacy Regulations 4-24-26\n"
                       "mbp.ms.gov/sites/default/files/2026-04/"
                       "Regulations%204-24-26.pdf"),
                 bg=BG, fg=DIM, font=FONT_BODY, wraplength=360,
                 justify="left").pack(padx=14, pady=(0, 8))

        bullets = [
            "C-II Prescriptions: Valid for 6 MONTHS. No refills permitted.",
            "C-III thru C-V: Valid for 6 MONTHS. Max 5 refills.",
            "Non-Controlled: Valid for 12 MONTHS.",
            "Emergency C-II: Pharmacist may fill oral authorization; hard copy must follow within 7 days.",
            "Transfers: C-II cannot be transferred. C-III thru C-V may be transferred ONCE (unless real-time DB).",
            "Record Keeping: All prescription records must be maintained for at least 6 YEARS per MS Law.",
            "Pseudoephedrine: Restricted behind counter. Logbook and ID required. State limits apply.",
        ]

        card = tk.Frame(host, bg=PANEL)
        card.pack(fill="x", padx=14, pady=8)
        for line in bullets:
            row = tk.Frame(card, bg=PANEL)
            row.pack(fill="x", padx=10, pady=4)
            tk.Label(row, text="•", bg=PANEL, fg=ACCENT,
                     font=FONT_BUTTON).pack(side="left", anchor="n",
                                            padx=(0, 6))
            tk.Label(row, text=line, bg=PANEL, fg=TEXT, font=FONT_BODY,
                     wraplength=320, justify="left",
                     anchor="w").pack(side="left", fill="x", expand=True)

    def panel_admin(self):
        # T5.3 — admin control. DB-backed. Admin-only guard.
        # Reuses db_add_user / db_remove_user / db_list_users / db_log_audit /
        # is_strong_pin. Inventory + AuditLog read inline (no helper churn).
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Admin Control", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)
        if not self.is_admin:
            tk.Label(host, text="Admin only.", bg=BG, fg=RED,
                     font=FONT_BUTTON).pack(pady=20)
            return

        # ---- Shift Notes Editor (T7.2) ----
        notes_card = tk.Frame(host, bg=PANEL)
        notes_card.pack(fill="x", padx=14, pady=8)
        tk.Label(notes_card, text="Shift Notes Editor", bg=PANEL,
                 fg=ACCENT, font=FONT_BUTTON).pack(
                     anchor="w", padx=10, pady=(8, 4))
        notes_txt = tk.Text(notes_card, bg=BG, fg=TEXT, font=FONT_BODY,
                            height=4, bd=0, wrap="word",
                            insertbackground=TEXT, padx=8, pady=6)
        notes_txt.pack(fill="x", padx=10, pady=2)
        notes_txt.insert(
            "1.0",
            db_get_state("shift_notes", "Welcome to your shift."))
        tk.Button(notes_card, text="Save Notes", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0,
                  command=lambda: self._admin_save_notes(
                      notes_txt.get("1.0", "end"))
                  ).pack(fill="x", padx=10, pady=(6, 10))

        # ---- Staff Roster ----
        roster = tk.Frame(host, bg=PANEL)
        roster.pack(fill="x", padx=14, pady=8)
        tk.Label(roster, text="Staff Roster", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
        admins, techs = db_list_users()
        for a in admins:
            tk.Label(roster, text="%s  (admin)" % a, bg=PANEL, fg=DIM,
                     font=FONT_BODY, anchor="w").pack(
                         anchor="w", padx=14, pady=2)
        for t in techs:
            row = tk.Frame(roster, bg=PANEL)
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, text=t, bg=PANEL, fg=TEXT, font=FONT_BODY,
                     anchor="w").pack(side="left", fill="x", expand=True,
                                       padx=4)
            # T7.13 — Audit shortcut: sets audit filter to this tech
            # and redraws. Compounds with T7.7's filter mechanism.
            tk.Button(row, text="Audit", bg=DIM, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda n=t: self._admin_audit_filter(n)
                      ).pack(side="right", padx=4)
            tk.Button(row, text="Remove", bg=RED, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda n=t: self._admin_remove_tech(n)
                      ).pack(side="right", padx=4)
        if not techs:
            tk.Label(roster, text="(no technicians)", bg=PANEL, fg=DIM,
                     font=FONT_BODY).pack(anchor="w", padx=14, pady=2)

        add_f = tk.Frame(roster, bg=PANEL)
        add_f.pack(fill="x", padx=10, pady=(8, 10))
        tk.Label(add_f, text="Add Technician:", bg=PANEL, fg=TEXT,
                 font=FONT_BODY).pack(anchor="w")
        name_e = tk.Entry(add_f, font=FONT_BODY, bg=BG, fg=TEXT,
                          insertbackground=TEXT)
        name_e.pack(fill="x", pady=2, ipady=4)
        tk.Label(add_f, text="Optional PIN (min 4):", bg=PANEL, fg=DIM,
                 font=FONT_BODY).pack(anchor="w", pady=(4, 0))
        pin_e = tk.Entry(add_f, font=FONT_BODY, bg=BG, fg=TEXT,
                         insertbackground=TEXT, show="*")
        pin_e.pack(fill="x", pady=2, ipady=4)
        tk.Button(add_f, text="Add Tech", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0,
                  command=lambda: self._admin_add_tech(
                      name_e.get(), pin_e.get())
                  ).pack(fill="x", pady=(6, 0))

        # ---- Class PTCB Readiness (T7.4) ----
        # Per-tech mastery against the BRAND_GENERIC pool. Color bands:
        # >=80 GREEN, >=50 ACCENT, <50 RED. Empty roster shows hint.
        cr = tk.Frame(host, bg=PANEL)
        cr.pack(fill="x", padx=14, pady=8)
        tk.Label(cr, text="Class PTCB Readiness", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
        if not techs:
            tk.Label(cr, text="(no technicians on roster)",
                     bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                         anchor="w", padx=14, pady=(2, 10))
        else:
            for t in techs:
                m_count, m_total, m_pct = ptcb_readiness(t)
                if m_pct >= 80:
                    col = GREEN
                elif m_pct >= 50:
                    col = ACCENT
                else:
                    col = RED
                tk.Label(
                    cr,
                    text="%s  —  %d / %d  (%d%%)" % (
                        t, m_count, m_total, m_pct),
                    bg=PANEL, fg=col, font=FONT_BODY,
                    anchor="w", wraplength=320, justify="left"
                ).pack(anchor="w", padx=14, pady=2)
            tk.Frame(cr, bg=PANEL, height=6).pack()

        # ---- Inventory / Expiration (T5.3 + T7.12 filter) ----
        inv = tk.Frame(host, bg=PANEL)
        inv.pack(fill="x", padx=14, pady=8)
        inv_header = ("Inventory / Expiration (filter: '%s')"
                      % self._inv_filter
                      if self._inv_filter
                      else "Inventory / Expiration")
        tk.Label(inv, text=inv_header, bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))

        # T7.12 — drug-name filter. Parameterized LIKE; case-insensitive
        # via SQLite default for ASCII.
        ifilt = tk.Frame(inv, bg=PANEL)
        ifilt.pack(fill="x", padx=10, pady=(2, 6))
        ifilt_e = tk.Entry(ifilt, font=FONT_BODY, bg=BG, fg=TEXT,
                           insertbackground=TEXT)
        ifilt_e.insert(0, self._inv_filter)
        ifilt_e.pack(side="left", fill="x", expand=True, ipady=4)
        tk.Button(ifilt, text="Find", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0,
                  command=lambda: self._admin_inv_filter(ifilt_e.get())
                  ).pack(side="left", padx=(6, 0))
        if self._inv_filter:
            tk.Button(ifilt, text="Clear", bg=DIM, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda: self._admin_inv_filter("")
                      ).pack(side="left", padx=(6, 0))

        conn = get_db_connection()
        try:
            if self._inv_filter:
                inv_rows = conn.execute(
                    "SELECT drug_name, exp_date FROM Inventory "
                    "WHERE drug_name LIKE ? "
                    "ORDER BY exp_date, drug_name",
                    ("%" + self._inv_filter + "%",)
                ).fetchall()
            else:
                inv_rows = conn.execute(
                    "SELECT drug_name, exp_date FROM Inventory "
                    "ORDER BY exp_date, drug_name"
                ).fetchall()
        finally:
            conn.close()
        if not inv_rows:
            empty_msg = ("(no matches)" if self._inv_filter
                         else "(no inventory)")
            tk.Label(inv, text=empty_msg, bg=PANEL, fg=DIM,
                     font=FONT_BODY).pack(anchor="w", padx=14, pady=2)
        for r in inv_rows:
            row = tk.Frame(inv, bg=PANEL)
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row,
                     text="%s — exp %s" % (r["drug_name"], r["exp_date"]),
                     bg=PANEL, fg=TEXT, font=FONT_BODY,
                     anchor="w").pack(side="left", fill="x", expand=True,
                                       padx=4)
            tk.Button(row, text="Remove", bg=RED, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda d=r["drug_name"]:
                          self._admin_remove_inv(d)
                      ).pack(side="right", padx=4)

        add_inv = tk.Frame(inv, bg=PANEL)
        add_inv.pack(fill="x", padx=10, pady=(8, 10))
        tk.Label(add_inv, text="Add Drug:", bg=PANEL, fg=TEXT,
                 font=FONT_BODY).pack(anchor="w")
        drug_e = tk.Entry(add_inv, font=FONT_BODY, bg=BG, fg=TEXT,
                          insertbackground=TEXT)
        drug_e.pack(fill="x", pady=2, ipady=4)
        tk.Label(add_inv, text="Expiration date (YYYY-MM-DD):",
                 bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                     anchor="w", pady=(4, 0))
        exp_e = tk.Entry(add_inv, font=FONT_BODY, bg=BG, fg=TEXT,
                         insertbackground=TEXT)
        exp_e.pack(fill="x", pady=2, ipady=4)
        tk.Button(add_inv, text="Add", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0,
                  command=lambda: self._admin_add_inv(
                      drug_e.get(), exp_e.get())
                  ).pack(fill="x", pady=(6, 0))

        # T7.16 — Inventory export (stock-count audit use).
        tk.Button(inv, text="Export Inventory",
                  bg=ACCENT, fg=BG, font=FONT_BUTTON, bd=0,
                  command=self._admin_export_inventory
                  ).pack(fill="x", padx=10, pady=(4, 10))

        # ---- Audit Log Viewer (T5.3 + T7.7 filter) ----
        log_f = tk.Frame(host, bg=PANEL)
        log_f.pack(fill="x", padx=14, pady=8)
        header = ("Audit Log (latest 50, filter: '%s')" % self._audit_filter
                  if self._audit_filter
                  else "Audit Log (latest 50)")
        tk.Label(log_f, text=header, bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))

        # T7.7 filter form. Matches user OR action via parameterized LIKE.
        filt_row = tk.Frame(log_f, bg=PANEL)
        filt_row.pack(fill="x", padx=10, pady=(2, 6))
        filt_e = tk.Entry(filt_row, font=FONT_BODY, bg=BG, fg=TEXT,
                          insertbackground=TEXT)
        filt_e.insert(0, self._audit_filter)
        filt_e.pack(side="left", fill="x", expand=True, ipady=4)
        tk.Button(filt_row, text="Filter", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0,
                  command=lambda: self._admin_audit_filter(filt_e.get())
                  ).pack(side="left", padx=(6, 0))
        if self._audit_filter:
            tk.Button(filt_row, text="Clear", bg=DIM, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda: self._admin_audit_filter("")
                      ).pack(side="left", padx=(6, 0))

        conn = get_db_connection()
        try:
            if self._audit_filter:
                like = "%" + self._audit_filter + "%"
                entries = conn.execute(
                    "SELECT timestamp, user, action FROM AuditLog "
                    "WHERE user LIKE ? OR action LIKE ? "
                    "ORDER BY id DESC LIMIT 50",
                    (like, like)
                ).fetchall()
            else:
                entries = conn.execute(
                    "SELECT timestamp, user, action FROM AuditLog "
                    "ORDER BY id DESC LIMIT 50"
                ).fetchall()
        finally:
            conn.close()
        if not entries:
            empty_msg = ("(no matches)" if self._audit_filter
                         else "(empty)")
            tk.Label(log_f, text=empty_msg, bg=PANEL, fg=DIM,
                     font=FONT_BODY).pack(anchor="w", padx=14, pady=(2, 10))
        for e in entries:
            tk.Label(log_f,
                     text="%s  %s  —  %s" % (
                         e["timestamp"], e["user"], e["action"]),
                     bg=PANEL, fg=TEXT, font=FONT_BODY, wraplength=340,
                     justify="left",
                     anchor="w").pack(anchor="w", padx=14, pady=1)

        # T7.9 — Export. Always exports the FULL AuditLog table, not
        # just the latest-50 view or the current filter.
        tk.Button(log_f, text="Export Full Audit Log",
                  bg=ACCENT, fg=BG, font=FONT_BUTTON, bd=0,
                  command=self._admin_export_audit
                  ).pack(fill="x", padx=10, pady=(10, 4))

        # T7.10 — DB backup. Full snapshot via online backup API.
        tk.Button(log_f, text="Backup Database",
                  bg=ACCENT, fg=BG, font=FONT_BUTTON, bd=0,
                  command=self._admin_backup_db
                  ).pack(fill="x", padx=10, pady=(0, 10))

        # ---- Backups (T7.14) ----
        # Lists pharmacy_backup_*.db files in home dir, newest first,
        # each with a Restore button. Restore is destructive: prompts
        # before overwriting live DB, then forces logout.
        bk = tk.Frame(host, bg=PANEL)
        bk.pack(fill="x", padx=14, pady=8)
        tk.Label(bk, text="Backups (Restore)", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
        backups = db_list_backups()
        if not backups:
            tk.Label(bk,
                     text="(no backups — use 'Backup Database' above)",
                     bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                         anchor="w", padx=14, pady=(2, 10))
        for fname, fpath, _ in backups:
            row = tk.Frame(bk, bg=PANEL)
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, text=fname, bg=PANEL, fg=TEXT,
                     font=FONT_BODY, anchor="w",
                     wraplength=240, justify="left").pack(
                         side="left", fill="x", expand=True, padx=4)
            tk.Button(row, text="Restore", bg=RED, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda p=fpath, n=fname:
                          self._admin_restore_db(p, n)
                      ).pack(side="right", padx=4)
        if backups:
            tk.Frame(bk, bg=PANEL, height=6).pack()

    # ---- admin mutation handlers (T5.3) ----
    def _admin_add_tech(self, name, pin):
        name = (name or "").strip()
        pin = (pin or "").strip()
        if not name:
            messagebox.showerror("Add Tech", "Name required.")
            return
        if pin:
            ok, reason = is_strong_pin(pin)
            if not ok:
                messagebox.showerror("Add Tech", reason)
                return
        if not db_add_user(name, "tech", pin if pin else None):
            messagebox.showerror(
                "Add Tech", "Name is reserved or invalid.")
            return
        db_log_audit(self.user, "Added tech: %s" % name)
        self.navigate_to("admin")

    def _admin_remove_tech(self, name):
        if not messagebox.askyesno(
                "Remove Tech",
                "Remove '%s' and their scores/mastery?" % name):
            return
        db_remove_user(name)
        db_log_audit(self.user, "Removed tech: %s" % name)
        self.navigate_to("admin")

    def _admin_add_inv(self, drug, exp):
        drug = (drug or "").strip()
        exp = (exp or "").strip()
        if not drug or not exp:
            messagebox.showerror(
                "Inventory", "Drug name and exp date required.")
            return
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO Inventory "
                "(drug_name, exp_date) VALUES (?, ?)", (drug, exp))
            conn.commit()
        finally:
            conn.close()
        db_log_audit(self.user, "Inventory add: %s exp %s" % (drug, exp))
        self.navigate_to("admin")

    def _admin_remove_inv(self, drug):
        conn = get_db_connection()
        try:
            conn.execute(
                "DELETE FROM Inventory WHERE drug_name=?", (drug,))
            conn.commit()
        finally:
            conn.close()
        db_log_audit(self.user, "Inventory remove: %s" % drug)
        self.navigate_to("admin")

    def _admin_save_notes(self, text):
        # T7.2 — persist shift notes via db_set_state. Strip the
        # trailing newline the Tk Text widget appends.
        cleaned = (text or "").strip()
        db_set_state("shift_notes", cleaned)
        db_log_audit(self.user, "Updated shift notes")
        messagebox.showinfo("Shift Notes", "Saved.")

    def _admin_audit_filter(self, text):
        # T7.7 — set the audit log filter (or clear if empty) and
        # re-render. SQL LIKE % wildcards are added at query time, not
        # stored, so user-typed % is treated as literal-ish through the
        # parameterized binding. No filter audit-log entry (would spam).
        self._audit_filter = (text or "").strip()
        self.navigate_to("admin")

    def _admin_inv_filter(self, text):
        # T7.12 — inventory drug-name filter. Same pattern as audit
        # filter: state attribute + redraw.
        self._inv_filter = (text or "").strip()
        self.navigate_to("admin")

    def _admin_export_inventory(self):
        # T7.16 — export inventory to tab-separated text. Audit-logs
        # the export. Same OSError handling pattern as T7.9.
        try:
            path = db_export_inventory()
        except OSError as exc:
            messagebox.showerror(
                "Export Failed", "Could not write file:\n%s" % exc)
            return
        db_log_audit(self.user, "Exported inventory to %s" % path)
        messagebox.showinfo(
            "Export Complete",
            "Inventory written to:\n%s" % path)
        self.navigate_to("admin")

    def _admin_export_audit(self):
        # T7.9 — export to plain text. Audit-logs the export action
        # itself (and the destination path) so the export is itself
        # traceable. messagebox confirms the path Scott / inspector
        # can find via Pydroid 3 Files browser.
        try:
            path = db_export_audit_log()
        except OSError as exc:
            messagebox.showerror(
                "Export Failed", "Could not write file:\n%s" % exc)
            return
        db_log_audit(self.user, "Exported audit log to %s" % path)
        messagebox.showinfo(
            "Export Complete",
            "Audit log written to:\n%s" % path)
        self.navigate_to("admin")

    def _admin_backup_db(self):
        # T7.10 — full SQLite online backup. Audit-logs the backup
        # action so the snapshot is itself traceable. sqlite3.Error
        # (db locked, disk full, perms) is the failure mode.
        try:
            path = db_backup()
        except (sqlite3.Error, OSError) as exc:
            messagebox.showerror(
                "Backup Failed", "Could not back up DB:\n%s" % exc)
            return
        db_log_audit(self.user, "Backed up DB to %s" % path)
        messagebox.showinfo(
            "Backup Complete",
            "Database snapshot written to:\n%s" % path)
        self.navigate_to("admin")

    def _admin_restore_db(self, backup_path, backup_name):
        # T7.14 — restore from snapshot. Destructive: overwrites the
        # live DB. Strong confirmation. Audit-logs the intent BEFORE
        # the restore (because the restored DB may not contain this
        # entry afterward). Forces logout — in-app state may not
        # match the new DB (different users, different lockout, etc).
        if not messagebox.askyesno(
                "Restore Database",
                "OVERWRITE the live database with:\n"
                "  %s\n\n"
                "Current data will be REPLACED with the snapshot. "
                "This cannot be undone (unless you have a newer "
                "backup). You will be logged out.\n\n"
                "Proceed?" % backup_name):
            return
        db_log_audit(self.user,
                     "Restoring DB from %s (pre-restore mark)"
                     % backup_name)
        try:
            db_restore(backup_path)
        except (sqlite3.Error, OSError) as exc:
            messagebox.showerror(
                "Restore Failed",
                "Live DB unchanged.\nError: %s" % exc)
            return
        messagebox.showinfo(
            "Restore Complete",
            "Database restored from:\n%s\n\nLogging out." % backup_name)
        self.logout()

    def panel_tpr(self):
        # T5.4 — TPR Insurance Guide. Static panel; verbatim 5 rows from
        # v13 (panel_tpr_resolver lines 1190-1196). ADR-C05: UNVERIFIED.
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="TPR (Third Party Rejection) Guide",
                 bg=BG, fg=TEXT, font=FONT_HEADING).pack(pady=12)
        tk.Label(host,
                 text="⚠ UNVERIFIED DATA — v13 source, not externally validated.",
                 bg=BG, fg=RED, font=FONT_BODY, wraplength=360,
                 justify="left").pack(padx=14, pady=(0, 8))

        tpr_data = [
            ("RTS (Refill Too Soon)",
             "Patient has remaining supply. Check last fill date + 75% usage."),
            ("PA (Prior Auth)",
             "Insurance requires doctor's justification. Fax MD and notify patient."),
            ("Plan Exclusion",
             "Drug not covered by plan. Suggest generic or discount card."),
            ("NDC Not Covered",
             "Specific brand/size not on formulary. Switch to covered NDC."),
            ("M/I ID or Group",
             "Insurance info is outdated. Ask patient for new card or use Findins."),
        ]
        card = tk.Frame(host, bg=PANEL)
        card.pack(fill="x", padx=14, pady=8)
        for code, detail in tpr_data:
            row = tk.Frame(card, bg=PANEL)
            row.pack(fill="x", padx=10, pady=6)
            tk.Label(row, text=code, bg=PANEL, fg=ACCENT,
                     font=FONT_BUTTON, anchor="w").pack(
                         anchor="w", padx=2)
            tk.Label(row, text=detail, bg=PANEL, fg=TEXT,
                     font=FONT_BODY, wraplength=320, justify="left",
                     anchor="w").pack(anchor="w", padx=10, pady=(2, 0))

    def panel_hotkeys(self):
        # T5.5 — IC+ Hotkeys. Static panel; verbatim 8 key/description
        # pairs from v13 (panel_hotkeys lines 1208-1213). Software workflow
        # reference, not clinical/law data — no UNVERIFIED banner per
        # ADR-C05 scope.
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Intercom Plus (IC+) Hotkeys",
                 bg=BG, fg=TEXT, font=FONT_HEADING).pack(pady=12)

        keys = [
            ("F9", "Patient Search"),
            ("F12", "Release to POS / Finish"),
            ("ALT + O", "Options Menu"),
            ("ALT + P", "Product Detail"),
            ("CTRL + X", "Exception Queue"),
            ("CTRL + S", "Scan Rx / Document"),
            ("Shift + F1", "TeamRx / Help"),
            ("ALT + R", "Ready Status Check"),
        ]
        card = tk.Frame(host, bg=PANEL)
        card.pack(fill="x", padx=14, pady=8)
        for k, desc in keys:
            row = tk.Frame(card, bg=PANEL)
            row.pack(fill="x", padx=10, pady=4)
            tk.Label(row, text=k, bg=PANEL, fg=GREEN,
                     font=FONT_BUTTON, width=12, anchor="w").pack(
                         side="left")
            tk.Label(row, text=desc, bg=PANEL, fg=TEXT,
                     font=FONT_BODY, wraplength=240, justify="left",
                     anchor="w").pack(side="left", fill="x", expand=True)

    def panel_partials(self):
        # T5.6 — Partial Fill Ledger. DB-backed. Lists open partials
        # (resolved=0), add new partial (drug, qty_owed, patient, date),
        # resolve button per row. Uses PartialFills table (schema in
        # init_db). Parametrized writes. Audit-logged.
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Partial Fill Ledger", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)

        # ---- open partials list ----
        list_card = tk.Frame(host, bg=PANEL)
        list_card.pack(fill="x", padx=14, pady=8)
        tk.Label(list_card, text="Open Partials", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
        conn = get_db_connection()
        try:
            rows = conn.execute(
                "SELECT id, drug, qty_owed, patient, date "
                "FROM PartialFills WHERE resolved=0 ORDER BY date DESC, id DESC"
            ).fetchall()
        finally:
            conn.close()
        if not rows:
            tk.Label(list_card,
                     text="All partials resolved. Inventory is clear.",
                     bg=PANEL, fg=DIM, font=FONT_BODY).pack(
                         anchor="w", padx=14, pady=(2, 10))
        for r in rows:
            row = tk.Frame(list_card, bg=PANEL)
            row.pack(fill="x", padx=10, pady=4)
            tk.Label(
                row,
                text="%s  —  qty owed: %s\n%s  (%s)" % (
                    r["drug"], r["qty_owed"], r["patient"], r["date"]),
                bg=PANEL, fg=TEXT, font=FONT_BODY, justify="left",
                anchor="w", wraplength=240).pack(
                    side="left", fill="x", expand=True, padx=4)
            tk.Button(row, text="Resolve", bg=GREEN, fg=BG,
                      font=FONT_BUTTON, bd=0,
                      command=lambda pid=r["id"]:
                          self._partial_resolve(pid)
                      ).pack(side="right", padx=4)

        # ---- add new partial ----
        add_card = tk.Frame(host, bg=PANEL)
        add_card.pack(fill="x", padx=14, pady=8)
        tk.Label(add_card, text="Add Partial", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))

        def fld(label):
            r = tk.Frame(add_card, bg=PANEL)
            r.pack(fill="x", padx=10, pady=3)
            tk.Label(r, text=label, bg=PANEL, fg=TEXT, font=FONT_BODY,
                     width=12, anchor="w").pack(side="left")
            e = tk.Entry(r, font=FONT_BODY, bg=BG, fg=TEXT,
                         insertbackground=TEXT)
            e.pack(side="left", fill="x", expand=True, ipady=4)
            return e

        e_drug = fld("Drug")
        e_qty = fld("Qty owed")
        e_pat = fld("Patient")
        e_date = fld("Date")
        e_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Button(add_card, text="Add to Ledger", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0,
                  command=lambda: self._partial_add(
                      e_drug.get(), e_qty.get(),
                      e_pat.get(), e_date.get())
                  ).pack(fill="x", padx=10, pady=(6, 10))

    def _partial_add(self, drug, qty, patient, date):
        drug = (drug or "").strip()
        patient = (patient or "").strip()
        date = (date or "").strip()
        try:
            qty_int = int(str(qty).strip())
            if qty_int <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messagebox.showerror(
                "Partial", "Qty owed must be a positive integer.")
            return
        if not drug or not patient or not date:
            messagebox.showerror(
                "Partial", "Drug, patient, and date are required.")
            return
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO PartialFills "
                "(drug, qty_owed, patient, date) VALUES (?, ?, ?, ?)",
                (drug, qty_int, patient, date))
            conn.commit()
        finally:
            conn.close()
        db_log_audit(self.user,
                     "Logged partial: %s for %s" % (drug, patient))
        self.navigate_to("partials")

    def _partial_resolve(self, pid):
        conn = get_db_connection()
        try:
            conn.execute(
                "UPDATE PartialFills SET resolved=1 WHERE id=?", (pid,))
            conn.commit()
        finally:
            conn.close()
        db_log_audit(self.user, "Resolved partial (ID: %s)" % pid)
        self.navigate_to("partials")

    def panel_vaccines(self):
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Vaccine Eligibility", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)
        f = tk.Frame(host, bg=PANEL)
        f.pack(fill="x", padx=14, pady=8)
        tk.Label(f, text="⚠ No vaccine eligibility data in v13 source.",
                 bg=PANEL, fg=RED, font=FONT_BUTTON,
                 wraplength=340, justify="left").pack(padx=10, pady=(10, 4))
        tk.Label(f,
                 text="This panel requires a data decision before it can be built.\n"
                      "Options: (a) source CDC/ACIP schedule data and build a "
                      "structured table, or (b) embed a static reference sheet. "
                      "Neither option existed in v13. Raise this as a T5 scope "
                      "item or leave as a labeled placeholder.",
                 bg=PANEL, fg=DIM, font=FONT_BODY,
                 wraplength=340, justify="left").pack(padx=10, pady=(0, 12))

    def panel_sig(self):
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="SIG Decoder", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)
        tk.Label(host, text="⚠ UNVERIFIED DATA — v13 source, not externally validated.",
                 bg=BG, fg=RED, font=FONT_BODY, wraplength=360,
                 justify="left").pack(padx=14, pady=(0, 8))

        inp_f = tk.Frame(host, bg=PANEL)
        inp_f.pack(fill="x", padx=14, pady=6)
        tk.Label(inp_f, text="SIG string:", bg=PANEL, fg=TEXT,
                 font=FONT_BODY).pack(anchor="w", padx=10, pady=(8, 2))
        entry = tk.Entry(inp_f, font=FONT_BODY, bg=BG, fg=TEXT,
                         insertbackground=TEXT)
        entry.pack(fill="x", padx=10, ipady=6, pady=(0, 4))

        res_box = tk.Text(host, bg=PANEL, fg=TEXT, font=FONT_BODY,
                          height=6, bd=0, state="disabled",
                          wrap="word", padx=8, pady=6)
        res_box.pack(fill="x", padx=14, pady=4)

        def decode():
            raw = entry.get().strip()
            if not raw:
                return
            tokens = raw.upper().split()
            lines = []
            for tok in tokens:
                meaning = SIG_ABBREVIATIONS.get(tok)
                if meaning:
                    lines.append("%s  →  %s" % (tok, meaning))
                else:
                    lines.append("%s  →  (not in reference)" % tok)
            res_box.config(state="normal")
            res_box.delete("1.0", "end")
            res_box.insert("end", "\n".join(lines))
            res_box.config(state="disabled")

        tk.Button(inp_f, text="Decode", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0, command=decode
                  ).pack(fill="x", padx=10, pady=(0, 10))

        # Full reference list
        ref = tk.Frame(host, bg=PANEL)
        ref.pack(fill="x", padx=14, pady=8)
        tk.Label(ref, text="Full Reference", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
        for abbr, meaning in sorted(SIG_ABBREVIATIONS.items()):
            tk.Label(ref, text="%s  —  %s" % (abbr, meaning),
                     bg=PANEL, fg=TEXT, font=FONT_BODY,
                     anchor="w").pack(anchor="w", padx=14, pady=1)

    def panel_lookup(self):
        host = self.make_scrollable(self.content_host)
        tk.Label(host, text="Drug Lookup", bg=BG, fg=TEXT,
                 font=FONT_HEADING).pack(pady=12)
        tk.Label(host, text="⚠ UNVERIFIED DATA — v13 source, not externally validated.",
                 bg=BG, fg=RED, font=FONT_BODY, wraplength=360,
                 justify="left").pack(padx=14, pady=(0, 8))

        inp_f = tk.Frame(host, bg=PANEL)
        inp_f.pack(fill="x", padx=14, pady=6)
        tk.Label(inp_f, text="Brand or generic name:", bg=PANEL, fg=TEXT,
                 font=FONT_BODY).pack(anchor="w", padx=10, pady=(8, 2))
        entry = tk.Entry(inp_f, font=FONT_BODY, bg=BG, fg=TEXT,
                         insertbackground=TEXT)
        entry.pack(fill="x", padx=10, ipady=6, pady=(0, 4))

        res_box = tk.Text(host, bg=PANEL, fg=TEXT, font=FONT_BODY,
                          height=8, bd=0, state="disabled",
                          wrap="word", padx=8, pady=6)
        res_box.pack(fill="x", padx=14, pady=4)

        def search():
            q = entry.get().strip().lower()
            if not q:
                return
            hits = [
                d for d in BRAND_GENERIC
                if q in d["brand"].lower() or q in d["generic"].lower()
            ]
            # T7.8 — mastery indicator (tech only). One bulk query for
            # all hit brands, build a set, decorate each result line.
            mastered = set()
            if hits and not self.is_admin:
                mastered = db_mastered_brands(
                    self.user, [d["brand"] for d in hits])
            lines = []
            if hits:
                for d in hits:
                    lines.append("Brand: %s  |  Generic: %s" % (
                        d["brand"], d["generic"]))
                    if not self.is_admin:
                        if d["brand"] in mastered:
                            lines.append("  ✓ Mastered")
                        else:
                            lines.append("  · Not yet mastered")
                    # check COMMON_RX_FLAGS against generic name
                    for drug, flag in COMMON_RX_FLAGS:
                        if drug in d["generic"].lower():
                            lines.append("  ⚠ RX FLAG: %s" % flag)
            else:
                lines.append("No match found for \"%s\"." % entry.get().strip())
            res_box.config(state="normal")
            res_box.delete("1.0", "end")
            res_box.insert("end", "\n".join(lines))
            res_box.config(state="disabled")

        tk.Button(inp_f, text="Search", bg=ACCENT, fg=BG,
                  font=FONT_BUTTON, bd=0, command=search
                  ).pack(fill="x", padx=10, pady=(0, 10))

        # Full list
        ref = tk.Frame(host, bg=PANEL)
        ref.pack(fill="x", padx=14, pady=8)
        tk.Label(ref, text="Full List (Brand → Generic)", bg=PANEL, fg=ACCENT,
                 font=FONT_BUTTON).pack(anchor="w", padx=10, pady=(8, 4))
        for d in sorted(BRAND_GENERIC, key=lambda x: x["brand"]):
            tk.Label(ref, text="%s  →  %s" % (d["brand"], d["generic"]),
                     bg=PANEL, fg=TEXT, font=FONT_BODY,
                     anchor="w").pack(anchor="w", padx=14, pady=1)

# ============================================================
# S5 — ENTRYPOINT
# Pydroid 3: open this .py and press Play. init_db() creates the
# fresh DB on first run (ADR-C01). No migrate_* calls.
# ============================================================
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = PharmacyApp(root)
    root.mainloop()
