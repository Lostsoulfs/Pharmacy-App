---
lifecycle: growing
frozen: false
visibility: public
data_verified: false
maturity: active-development
updated: 2026-06-20
---

# Status — Pharmacy-App

> **Training software only.** Clinical and legal content is **UNVERIFIED** and must not be used
> for patient care or professional decisions (see [`docs/OFFICIAL_SOURCES_2026.md`](docs/OFFICIAL_SOURCES_2026.md)).
> This file makes no medical, clinical, or safety claim.

**This project is GROWING, not frozen.** It is a single-user, offline PTCB-prep training app for
one technician (Nathan). It will keep gaining content and polish until it is explicitly marked
`frozen: true` in the front-matter above. Treat anything here as a current snapshot, not a release.

This file is the lifecycle source-of-truth referenced by `AGENTS.md` (source-of-truth order #3,
alongside `docs/LEARNINGS.md`).

## Lifecycle

- **lifecycle:** `growing` — actively developed; expect change.
- **frozen:** `false` — no freeze declared.
- **visibility:** `public` — code only; no PHI/PII ever (SECURITY.md).
- **data_verified:** `false` — clinical/law datasets are pending pharmacist sign-off (ADR-C05); the
  in-code `DATA_VERIFIED` keys stay `False` until then.

## Current state

A Python/Tkinter training app (desktop + Android via Pydroid 3), zero runtime dependencies. Quiz
training (SM-2), reference tools, an admin console, and clinical **calculators** (insulin/days-supply,
DEA checksum, Cockcroft-Gault CrCl, Mosteller BSA, pediatric dosing).

Verification baseline (full code audit, 2026-05-21 — see `docs/audits/`): 99 tests passing; branch
coverage `logic.py` 90% / `data.py` 96% / `app.py` 0% (UI, 846 untested stmts) — total ~34%;
mutation 630 mutants / 415 killed on `logic.py`; ruff style-debt only (0 pyflakes); 0 high-severity
defects, 4 medium + 8 low recorded (fixes deferred). Governance is full: AGENTS/CLAUDE/SECURITY,
secret/PII pre-commit + CI scan, CodeQL, dependency review, OpenSSF scorecard, control audit,
multi-version test matrix.

## Memory & decisions

- **Tool gotchas:** [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md).
- **Project learnings:** [`docs/LEARNINGS.md`](docs/LEARNINGS.md).
- **Audits:** [`docs/audits/`](docs/audits/). Decisions are recorded inline in `AGENTS.md`
  (ADR-C01, ADR-C05, F-06, …) by design — no separate `docs/adr/`.

## Backlog

Deferred work and known gaps are parked in [`docs/BACKLOG.md`](docs/BACKLOG.md).

## Scope (unchanged)

Offline single-user **training** app. No real patient care, no PHI/PII, no payments, no network at
runtime. The clinical calculators are study aids, not a validated clinical tool, and are **not**
advertised as an external/agent capability (that decision is gated on pharmacist sign-off — see the
backlog).
