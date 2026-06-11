"""Data layer — fresh DB, schema, CRUD; NO migration.

T2 baseline: no migrate_* functions, no LEGACY_JSON, fresh DB.
All writes parameterized. Headlessly testable (sqlite only, no tkinter).
"""

import os
import sqlite3
from datetime import datetime, timedelta

from .config import DB_FILE, MAX_LOG_ENTRIES, RESERVED_TECH_NAMES
from .logic import hash_pin
from .clinical_data import BRAND_GENERIC


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
                ease_factor REAL,
                interval_days INTEGER,
                last_reviewed TEXT,
                repetitions INTEGER,
                PRIMARY KEY (tech_name, drug_name)
            );
            """
        )
        # SRS columns (2026-05-20). Forward-only additive migration for
        # DBs created under the pre-SRS MasteryStats schema — ADR-C01
        # keeps no migration subsystem, but a one-shot ADD COLUMN is
        # safe and idempotent. "duplicate column name" means a fresh DB
        # already has it via the CREATE TABLE above; ignore only that.
        for col, decl in (("ease_factor", "REAL"),
                          ("interval_days", "INTEGER"),
                          ("last_reviewed", "TEXT"),
                          ("repetitions", "INTEGER")):
            try:
                conn.execute(
                    "ALTER TABLE MasteryStats ADD COLUMN %s %s"
                    % (col, decl))
            except sqlite3.OperationalError as exc:
                if "duplicate column name" not in str(exc):
                    raise
        cur = conn.execute("SELECT COUNT(*) FROM Users WHERE role='admin'")
        if cur.fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO Users (name, role, pin_hash) VALUES (?, ?, ?)",
                ("DefaultAdmin", "admin", hash_pin("1234")),
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
    given. Returns True on success, False if name reserved/blank OR
    if name already exists with a DIFFERENT role (A1 fix: prevents
    silent admin demotion via tech-add name collision)."""
    if not name or not name.strip():
        return False
    if name.strip().lower() in RESERVED_TECH_NAMES:
        return False
    cleaned = name.strip()
    conn = get_db_connection()
    try:
        # A1 fix: reject if the name exists with a different role.
        # Without this, db_add_user("DefaultAdmin", "tech") silently
        # overwrites the existing admin DefaultAdmin via INSERT OR REPLACE.
        existing = conn.execute(
            "SELECT role FROM Users WHERE name=?", (cleaned,)
        ).fetchone()
        if existing and existing["role"] != role:
            return False
        conn.execute(
            "INSERT OR REPLACE INTO Users (name, role, pin_hash) "
            "VALUES (?, ?, ?)",
            (cleaned, role, hash_pin(pin) if pin else None),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def db_remove_user(name):
    """Cascading delete: user + their scores + mastery rows.
    A3 fix 2026-05-19: refuses if removing this name would leave zero
    admins (last-admin guard). Returns True on success, False if the
    delete would leave zero admins (caller should surface the reason)."""
    conn = get_db_connection()
    try:
        # A3 fix: last-admin guard
        row = conn.execute(
            "SELECT role FROM Users WHERE name=?", (name,)
        ).fetchone()
        if row and row["role"] == "admin":
            admin_count = conn.execute(
                "SELECT COUNT(*) AS c FROM Users WHERE role='admin'"
            ).fetchone()["c"]
            if admin_count <= 1:
                return False
        conn.execute("DELETE FROM Users WHERE name=?", (name,))
        conn.execute("DELETE FROM Scores WHERE tech_name=?", (name,))
        conn.execute("DELETE FROM PTCBMastery WHERE tech_name=?", (name,))
        conn.execute("DELETE FROM MasteryStats WHERE tech_name=?", (name,))
        conn.commit()
        return True
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


def db_user_has_pin(name):
    """True if the named user exists and has a PIN set. Lets the UI
    decide whether to prompt for a PIN before login."""
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT pin_hash FROM Users WHERE name=?", (name,)
        ).fetchone()
    finally:
        conn.close()
    return bool(row and row["pin_hash"])


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
            (tech, datetime.now().strftime("%Y-%m-%d"),
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


def _like_escape(s):
    """A5 fix. Escape SQL LIKE wildcards (%, _) so user-typed text
    is treated as literal. Returns the escaped string; caller must
    use ESCAPE '\\' clause in the LIKE query."""
    if not s:
        return s
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _date_is_valid(s):
    """A4 helper. Returns True iff s parses as a real calendar date
    under %Y-%m-%d. Used after regex check enforces zero-padding."""
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


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


# ---- panel-facing read helpers (extracted from app.py, finding M1) ----

def db_inventory_expiring(within_days=30, today=None):
    """Inventory rows whose exp_date falls on or before
    today + within_days, soonest first. `today` defaults to now;
    a 'YYYY-MM-DD' string is also accepted (for deterministic tests).
    Returns list of (drug_name, exp_date)."""
    if today is None:
        base = datetime.now()
    elif isinstance(today, str):
        base = datetime.strptime(today, "%Y-%m-%d")
    else:
        base = today
    cutoff = (base + timedelta(days=within_days)).strftime("%Y-%m-%d")
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT drug_name, exp_date FROM Inventory "
            "WHERE exp_date <= ? ORDER BY exp_date ASC, drug_name ASC",
            (cutoff,)
        ).fetchall()
    finally:
        conn.close()
    return [(r["drug_name"], r["exp_date"]) for r in rows]


def db_inventory_list(name_filter=""):
    """All Inventory rows ordered by exp_date then drug_name. When
    name_filter is non-empty, restrict to drug_name LIKE %filter%
    with LIKE wildcards escaped. Returns list of (drug_name,
    exp_date)."""
    conn = get_db_connection()
    try:
        if name_filter:
            pat = "%" + _like_escape(name_filter) + "%"
            rows = conn.execute(
                "SELECT drug_name, exp_date FROM Inventory "
                "WHERE drug_name LIKE ? ESCAPE '\\' "
                "ORDER BY exp_date, drug_name",
                (pat,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT drug_name, exp_date FROM Inventory "
                "ORDER BY exp_date, drug_name"
            ).fetchall()
    finally:
        conn.close()
    return [(r["drug_name"], r["exp_date"]) for r in rows]


def db_audit_log(text_filter="", limit=50):
    """Most recent AuditLog rows, newest first, capped at `limit`.
    When text_filter is non-empty, match user OR action LIKE
    %filter% with LIKE wildcards escaped. Returns list of
    (timestamp, user, action)."""
    conn = get_db_connection()
    try:
        if text_filter:
            like = "%" + _like_escape(text_filter) + "%"
            rows = conn.execute(
                "SELECT timestamp, user, action FROM AuditLog "
                "WHERE user LIKE ? ESCAPE '\\' "
                "OR action LIKE ? ESCAPE '\\' "
                "ORDER BY id DESC LIMIT ?",
                (like, like, int(limit))
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT timestamp, user, action FROM AuditLog "
                "ORDER BY id DESC LIMIT ?",
                (int(limit),)
            ).fetchall()
    finally:
        conn.close()
    return [(r["timestamp"], r["user"], r["action"]) for r in rows]


def db_open_partials():
    """Open (resolved=0) partial fills, newest first. Returns list
    of (id, drug, qty_owed, patient, date)."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT id, drug, qty_owed, patient, date FROM PartialFills "
            "WHERE resolved=0 ORDER BY date DESC, id DESC"
        ).fetchall()
    finally:
        conn.close()
    return [(r["id"], r["drug"], r["qty_owed"], r["patient"], r["date"])
            for r in rows]


# ---- panel-facing write helpers (extracted from app.py, finding M1) ----

def db_mark_mastered(tech_name, drug_name):
    """Record that a tech has mastered a drug. Idempotent — a repeat
    call is a no-op via INSERT OR IGNORE on the composite key."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO PTCBMastery (tech_name, drug_name) "
            "VALUES (?, ?)",
            (tech_name, drug_name),
        )
        conn.commit()
    finally:
        conn.close()


def db_get_mastery_stats(tech_name, drug_name):
    """Return one tech+drug MasteryStats row as a plain dict (total,
    correct, ease_factor, interval_days, repetitions), or None if the
    card has never been seen. The caller feeds this into
    logic.sm2_update to compute the next review schedule."""
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT total, correct, ease_factor, interval_days, "
            "repetitions FROM MasteryStats "
            "WHERE tech_name=? AND drug_name=?",
            (tech_name, drug_name),
        ).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def db_upsert_mastery_stats(tech_name, drug_name, total, correct,
                            ease_factor, interval_days, repetitions,
                            last_reviewed):
    """Insert or replace a MasteryStats row. The caller computes the
    running total/correct and the new SRS values (logic.sm2_update);
    this helper persists the full row on the (tech, drug) key."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO MasteryStats "
            "(tech_name, drug_name, correct, total, ease_factor, "
            "interval_days, last_reviewed, repetitions) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (tech_name, drug_name, correct, total, ease_factor,
             interval_days, last_reviewed, repetitions),
        )
        conn.commit()
    finally:
        conn.close()


def db_add_inventory(drug_name, exp_date):
    """Add or replace an Inventory row. Caller validates exp_date as
    strict zero-padded ISO YYYY-MM-DD before calling."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO Inventory (drug_name, exp_date) "
            "VALUES (?, ?)",
            (drug_name, exp_date),
        )
        conn.commit()
    finally:
        conn.close()


def db_remove_inventory(drug_name):
    """Delete an Inventory row by drug name. No-op if absent."""
    conn = get_db_connection()
    try:
        conn.execute(
            "DELETE FROM Inventory WHERE drug_name=?", (drug_name,))
        conn.commit()
    finally:
        conn.close()


def db_add_partial(drug, qty_owed, patient, date):
    """Append a partial-fill ledger row (resolved=0 by default).
    Caller validates qty_owed (positive int) and date format first."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO PartialFills (drug, qty_owed, patient, date) "
            "VALUES (?, ?, ?, ?)",
            (drug, qty_owed, patient, date),
        )
        conn.commit()
    finally:
        conn.close()


def db_resolve_partial(pid):
    """Mark an open partial fill resolved. Returns True iff a row
    actually changed — False if the id was already resolved or is no
    longer on the ledger — so the caller can decide whether to
    audit-log the action."""
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "UPDATE PartialFills SET resolved=1 "
            "WHERE id=? AND resolved=0", (pid,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
