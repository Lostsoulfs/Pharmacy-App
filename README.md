# Pharmacy-App

> Training software only. Clinical and legal content is unverified and must not
> be used for patient care or professional decisions. See
> [Official Source Boundary](docs/OFFICIAL_SOURCES_2026.md).

A pharmacy-technician PTCB-prep training app. Single-user, offline,
SQLite-backed. Runs on Android via Pydroid 3 (Tkinter) and on the
desktop.

## Features

- **Quiz training** — Top 200 brand/generic, red-flag scenarios, LASA
  pairs, and an SM-2 spaced-repetition hard mode.
- **Clinical calculators** — insulin days supply, days supply, DEA
  checksum, Cockcroft-Gault CrCl, Mosteller BSA, pediatric dosing.
- **Reference tools** — SIG decoder, drug lookup, vaccine
  eligibility, partial-fill ledger, TPR insurance guide, IC+ hotkeys.
- **Admin console** — staff roster, inventory/expiration, audit log,
  database backup and restore.
- **Shift dashboard** — expiration alerts, performance, PTCB
  readiness, weak spots.

## Run

- **Desktop:** `python main.py` from the repo root (Python 3.11+ with
  Tkinter).
- **Android (Pydroid 3):** open `main.py` and press Play.

The app needs no third-party packages at runtime.

## Develop and test

    pip install -r requirements-dev.txt
    pytest -q      # the test suite
    nox            # lint (pyflakes) + types + tests
    nox -l         # list every session

## Documentation

- `AGENTS.md` — architecture, conventions, and the agent contract
  (`CLAUDE.md` is only Claude-specific notes and points there).
- `TESTING_PLAYBOOK.md` — the layered testing methodology.
- `KNOWN_ISSUES.md` — tooling caveats.
- `docs/OFFICIAL_SOURCES_2026.md` — authoritative source boundary for
  future qualified content review.
- `docs/DATA_SOURCE_REGISTER_2026.md` — dataset-key to source-family
  mapping; review-routing metadata only.
- `docs/adr/` — durable repository and clinical/legal boundary decisions.
- `docs/LEARNINGS.md` — dated gotchas and upgrade-campaign findings.
- `docs/audits/` — data and code audit reports.

## Status

Clinical and law datasets are **UNVERIFIED** pending pharmacist
sign-off (ADR-C05). The 2026-05-20 audits in `docs/audits/` are
complete, but `config.DATA_VERIFIED` keeps every dataset flagged
unverified until a pharmacist signs each audit. The Tkinter UI
(`pharmacy_app/app.py`) has no automated test coverage — UI changes
require an on-device check on Pydroid 3 or desktop.
