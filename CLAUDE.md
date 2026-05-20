# CLAUDE.md

Pharmacy-technician PTCB-prep training app. Runs on Android via
Pydroid 3 (Tkinter) and on desktop. Single user, offline, SQLite.

## Architecture

- `main.py` — entry point.
- `pharmacy_app/app.py` — Tkinter UI; every panel. Currently 0% test
  coverage — the main remaining risk.
- `pharmacy_app/logic.py` — pure functions (calculators, PIN hashing,
  DEA check, answer matching). Fully tested and mutation-tested.
- `pharmacy_app/data.py` — SQLite layer. All DB access; parametrized
  queries only.
- `pharmacy_app/clinical_data.py` — static reference datasets.
- `pharmacy_app/config.py` — constants and the `DATA_VERIFIED` map.
- `pharmacy_app/theme.py` — colors and fonts.

## Conventions and rules

- Python 3.11 target (`ruff` `target-version = py311`). Keep syntax
  compatible with whatever Pydroid 3 ships on the user's device.
- `ruff check pharmacy_app` is the linter; 79-char lines. The repo
  carries pre-existing lint debt — do not fix it wholesale; just do
  not add new pyflakes (`F`) errors.
- ADR-C01: there is no DB migration subsystem — additive
  `ALTER TABLE` only.
- ADR-C05 / `DATA_VERIFIED`: clinical and law data is UNVERIFIED
  until a pharmacist confirms it. Each dataset has a key in
  `config.DATA_VERIFIED`; panels render an UNVERIFIED banner via
  `_unverified_banner(host, [domain_keys])` until every listed key
  is `True`. Flipping a key is a clinical assertion — only do it
  after a documented audit under `docs/audits/`.
- Never invent clinical facts. Verify against authoritative sources
  and cite them.

## Testing

- `pytest -q` runs the suite. Layers: example tests, Hypothesis
  property tests, branch coverage, mutmut mutation testing — see
  `TESTING_PLAYBOOK.md` for the order of effort.
- `nox` runs lint + types + tests; `nox -s coverage` / `seedsweep` /
  `mutation` for the full sweep.
- "Done" = `pytest` green and no new ruff `F` errors. UI changes also
  need an on-device check (Pydroid/desktop) — Tkinter cannot run in
  CI or this container.
- Known tooling bugs are recorded in `KNOWN_ISSUES.md` (e.g. the
  mutmut 3.5.0 multiprocessing crash).

## Environment

- Cloud/CI containers are ephemeral — commit and push or the work is
  lost.
- GitHub (`lostsoulfs/pharmacy-app`) is the backup of record.
