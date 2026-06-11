# Full Code Audit — Pharmacy-App

- **Scope:** application code (`app.py`, `logic.py`, `data.py`,
  `config.py`, `theme.py`, `main.py`), test-suite quality, tooling &
  docs.
- **Out of scope:** clinical/law data facts — not re-verified here.
  Items noticed in passing are listed in section 7 for the
  pharmacist (Nate).
- **Audit date:** 2026-05-21
- **Auditor:** Claude Code (`claude-opus-4-7`)
- **Constraint:** NO code was changed. This audit produces
  documentation only; fixes are deferred to a later session.
- **Status:** COMPLETE — no high-severity defects found; 4 medium
  and 8 low findings recorded; 4 recon leads rejected as false
  positives.

## 1. Methodology

Three read-only surveys produced candidate findings; **every finding
was then independently confirmed by reading the cited code** before
entering this report. Spot-checks disproved three survey claims
outright (section 6), so the discipline mattered. Baselines were
captured by running the suite, coverage, lint, and a full mutation
run. The codebase is small (≈4,500 lines) and was read in full.

## 2. Baseline facts (2026-05-21)

| Metric | Value |
|--------|-------|
| Tests | 99 passing, 6 files, 0 failures |
| Coverage (branch) | `logic.py` 90%, `data.py` 96%, `config.py`/`clinical_data.py` ~100%, `app.py` 0%, `theme.py` 0% — TOTAL 34% |
| Lint (`ruff check pharmacy_app`) | 291 errors — all pre-existing E/W style debt; **0 pyflakes (`F`) errors** |
| Mutation (`mutmut run`, mutates `logic.py`) | 630 mutants — 415 killed, 215 survived |

The 34% total is dominated by `app.py` (846 untested statements);
`theme.py` 0% is benign (pure constants, only imported by `app.py`).

## 3. Findings — Medium

| ID | Location | Finding | Recommended fix (not applied) |
|----|----------|---------|-------------------------------|
| M1 | `app.py` `panel_home` 311-319, `panel_admin` 1021-1037 & 1110-1126, `panel_partials` 1437-1442 | Inline `conn.execute` SQL embedded in UI panels bypasses the data layer. Contradicts `CLAUDE.md` ("`data.py` — All DB access"). Queries **are** parameterized — no security issue — but they are untestable and architecturally inconsistent. | Extract to `data.py` helpers (e.g. `db_expiring_inventory(within_days)`, `db_search_inventory(pat)`, `db_audit_log(filter, limit)`, `db_open_partials()`). Also lifts testable coverage (see §5). |
| M2 | `app.py` `_partial_add` 1495-1522 | Inconsistent date validation. `_admin_add_inv` strictly validates `exp_date` (regex + `strptime`, the A4 fix); `_partial_add` accepts **any** non-empty string for `date`. `PartialFills.date` is then sorted lexicographically (`ORDER BY date DESC`), so a non-ISO date sorts wrong. The field is pre-filled with today's ISO date, so the common path is safe — but the user can edit it freely. | Apply the same `re.fullmatch(r"\d{4}-\d{2}-\d{2}", ...)` + `_date_is_valid()` check used in `_admin_add_inv`. |
| M3 | `app.py` `check_answer` 605-609 & 632-635, `launch_quiz` 513 | Silent exception swallowing hides data loss. `except Exception: pass` around the mastery-stats write, the score save, and the hard-mode weighting query. On a locked/corrupt DB the tech's quiz progress and scores vanish with no banner and no audit entry — the user believes progress is tracked. Comments call these "non-critical" (a defensible product call), but the silence misleads the user. | Narrow `except Exception` to `sqlite3.Error`; surface a one-line non-blocking notice and/or write a failure marker to `AuditLog`. |
| M4 | `noxfile.py` 19-24 vs. `CLAUDE.md` quality gate | `nox -s lint` runs `ruff check .` / `ruff format --check .`, which fail on the 291 pre-existing E/W errors — so the default `nox` (lint, types, tests) is red. The real gate per `CLAUDE.md` is "pytest green + no new `F` errors," which the `lint` session does not express. | Either baseline the existing E/W debt in `ruff` config (e.g. per-file ignores or a noqa baseline), or narrow the `lint` session to `--select F` so it matches the documented gate. |

## 4. Findings — Low

| ID | Location | Finding |
|----|----------|---------|
| L1 | `app.py` `make_scrollable` 91-94 | Global `canvas.bind_all("<MouseWheel>")` is rebound by every panel; the surviving binding closes over the newest canvas. Works today (every panel calls `make_scrollable`) but is fragile, and `<MouseWheel>` never fires on the Android touch target. Recommend a widget-local `canvas.bind(...)` plus touch-drag handling (the "Scott to verify" comment at line 90). |
| L2 | `data.py` `db_list_backups` 285-296 | OSError on listing the home dir is swallowed, returning `[]` — an inaccessible home dir silently shows "no backups." Defensible, low impact. |
| L3 | `app.py` `_force_pin_change` 156-180 | Inescapable `while True` (cannot cancel) — by design, but on Android the only exit if the user is stuck is killing the app. |
| L4 | `app.py` `_admin_fails` 48 | The admin fail-counter is in-memory and resets on app restart; only the lockout *timestamp* persists. Documented tradeoff; acceptable for a single-user offline app. |
| L5 | `theme.py` 11-13 | Fonts hardcode "Segoe UI" (a Windows font); Tk silently substitutes on Pydroid 3 / Android. Cosmetic. |
| L6 | `app.py` `panel_lookup` 1679-1681 | RX-flag matching uses substring containment (`drug in d["generic"].lower()`), which can false-positive on short flag names. Logic is fragile; correctness depends on `COMMON_RX_FLAGS` content (see §7). |
| L7 | `main.py` 18-22 | `init_db()` runs before `tk.Tk()`; a DB failure crashes with a bare traceback and no dialog. Minor for a single-user app. |
| L8 | `data.py` `get_db_connection` 22 | `PRAGMA foreign_keys=ON` is set, but no table declares a `FOREIGN KEY` — cascade deletes are done manually in `db_remove_user`. The pragma is a no-op; a future user-scoped table will need a manual delete added or rows will orphan. Maintainability note. |

## 5. Test-suite assessment

- **99 tests across 6 files, all green.** `logic.py` (90%) and
  `data.py` (96%) are strongly covered, including most defensive
  branches. Property tests (Hypothesis) and a 50-seed sweep session
  are configured.
- **`app.py` UI is 0% executable coverage** — Tkinter cannot run
  headless in CI or this container. `test_app_banners.py` adds
  static AST validation of banner wiring only. This is the single
  largest test gap and is acknowledged in `CLAUDE.md`.
- **Mutation:** 215 of 630 `logic.py` mutants survived (~34%).
  Sampling shows the large majority are `raise ValueError("msg")` →
  `ValueError(None)` or message-text mutations that survive because
  tests assert *that* an exception raises, not its exact message —
  expected, low-value noise (asserting exact error text is brittle
  and generally discouraged). A minority are genuine mild gaps
  (default-argument flips, e.g. `is_female=False`,
  `priming_units_per_day=0`). **Conclusion: `logic.py` behavior is
  well-covered; the survivor count does not indicate real defects.**
  mutmut 3.x generates noisier mutants than the 3.4.x line the suite
  was originally tuned against.
- **Recommendation for `app.py`:** a headless rendering test is not
  feasible. The highest-value path is M1 — extracting inline SQL and
  quiz-state logic into `data.py`/helper functions makes that logic
  unit-testable and lifts real coverage. A mock-tkinter test would
  be fragile and low value; on-device manual checks remain the ADR
  position for actual rendering.

## 6. Rejected — recon false positives

| ID | Claim | Verdict |
|----|-------|---------|
| R1 | `calc_crcl` lets `SCr = 0` slip past validation | **FALSE.** `logic.py:180` `if scr <= 0` rejects 0 and negatives. |
| R2 | Hard-mode quiz crashes on empty / all-zero weights | **FALSE.** `BRAND_GENERIC` is a non-empty constant; `calculate_weight` floors its result at `max(1, …)`, so weights are always ≥ 1. |
| R3 | `data.py` ALTER TABLE `%`-formatting is SQL injection / an ADR-C01 violation | **FALSE.** SQLite cannot bind DDL identifiers with `?`; `%`-formatting hardcoded column names (`data.py:92-99`) is the only correct form, and the values are a hardcoded tuple. The ALTER loop is additive and idempotent — ADR-C01 compliant. |
| R4 | `db_log_audit` has a transaction race (DELETE can fail while INSERT commits) | **FALSE.** Both statements run inside one implicit `sqlite3` transaction; `conn.commit()` commits them atomically, and an exception before commit rolls the INSERT back on close. |

## 7. For pharmacist review (Nate)

This audit did **not** verify clinical or law facts. Per ADR-C05 the
pharmacist remains the authority. Items noticed in passing, worth a
second look:

- **HB1675 staffing-ratio** entry in `LAW_BULLETS` — cited "as
  introduced," effective 2026-07-01. Re-verify after that date that
  it was codified as enacted (already flagged in
  `law_tpr_audit_2026-05-20.md`).
- **`BRAND_GENERIC`** header is labeled "Top 200" but the list has
  210 entries (label vs. count; noted in
  `brand_generic_audit_2026-05-20.md`).
- **Zantac** carries a "withdrawn 2020" historical note — confirm it
  belongs in a current Top-200 study list.
- **`COMMON_RX_FLAGS`** is matched by substring against generic
  names (L6) — review whether each flag entry is specific enough not
  to mis-fire.
- All 8 `DATA_VERIFIED` keys are dated 2026-05-20; this code audit
  does not re-assert that clinical correctness.

## 8. Prioritized fix backlog (future session)

1. **M2** — add ISO-date validation to `_partial_add` (small, real bug).
2. **M3** — surface or log silent quiz-write failures.
3. **M1** — extract inline panel SQL into `data.py` helpers (also
   enables unit tests; addresses §5).
4. **M4** — reconcile the `noxfile` lint session with the documented
   quality gate.
5. **L1** — widget-local mouse binding + Pydroid touch scroll.
6. **Docs** — write a real `README.md`; correct `CLAUDE.md`
   ("`data.py` — All DB access" contradicted by M1; soften
   "`logic.py` … Fully tested and mutation-tested"); align the
   `requirements-dev.txt` mutmut comment with the corrected
   `KNOWN_ISSUES.md` entry.
7. **L2-L8** — opportunistic cleanup.

`KNOWN_ISSUES.md` needs no new entry — no new external tool bug
surfaced (the mutmut 3.5.0 entry was already corrected 2026-05-21).

## Sign-off

- Code audit (sections 1-6, 8): Claude Code, 2026-05-21 — automated
  review, no code changed.
- Clinical/law items (section 7): __________________________
  (qualified pharmacist) — date: ____________
