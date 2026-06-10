# UI Testing Notes — 2026-05-21

Source: hands-on testing of the app in Thonny on desktop. These are
observations and requested changes recorded for a **future patch
session** — nothing here has been actioned, and no code was changed.
Companion to `docs/audits/code_audit_2026-05-21.md`.

## Cross-cutting — input length / hard caps

- **No input field anywhere caps its length** (letters, numbers, or
  special characters). Flagged as a possible arbitrary-input risk.
  - Auditor note: the app uses parameterized SQL (no injection — see
    code audit) and never `eval`s input, so this is not a confirmed
    code-execution hole. Length caps are still worth adding as
    robustness / defense-in-depth (DB bloat, UI breakage).
- Future patch: cap every field at *(longest legitimate value + 2)*.
  For text — drug name, SIG code, Partial Fill Ledger fields — cap
  near the longest legal personal name in the US. **Do not hardcode
  the actual record-longest name** unless industry peers do the same;
  just pick a sane limit.
- Every numeric field (PIN, calculators, etc.) also needs a hard
  length cap. Caps need not be identical across fields unless making
  them uniform is safer. Candidate ~40 (unconfirmed — safe maximum
  still to be determined). Rationale: nobody needs a million of one
  item, but large unit counts can be legitimate (e.g. an insurance
  measure) — limits must not block real use.

## Partial Fill Ledger

- Accepts gibberish (e.g. `sdsdf`) in text fields — want a way to
  require real / plausible words.
- Patient names **must still allow misspellings** — genuine accidental
  typos should be accepted and saved as-is; do not over-restrict.
- **No edit function — only delete.** Fixing a typo currently means
  deleting the whole entry and re-creating it. Add an edit capability.
- Rename the row buttons to plain **"Edit"** and **"Delete"**.
  "Resolve" was unclear — the tester could not tell if it meant edit
  or delete. Caveat: the tester is not in the field, so "Resolve" may
  be correct pharmacy terminology — confirm before changing.
- If correct pharmacy terminology is unknown, gather authoritative
  wording so the lingo matches what an MS Walgreens pharmacist expects.

## SIG Decoder

- Should reject random numbers / junk input.
- Should offer a way to add more entries / fill in more info.
- When a code is not in the reference, do something clearer than the
  current "(not in reference)" filler line at the bottom — e.g. an
  error message. Do not render filler text.

## Vaccine Eligibility & TPR Insurance Guide

- Should scroll with the **mouse wheel** and with the **up/down arrow
  keys**. (Matches code-audit finding **L1** — confirmed by hands-on
  testing.)

## Calculators

- Correctly reject fake numbers and invalid combinations (good).
- But still accept far more digits than needed. Cap each field's
  input length at the largest plausible value before showing the
  limit / error message.
- The DEA field should cap at the maximum DEA-number length.

## Test files do not run in Thonny

- No test file runs in Thonny — each reports "no module named
  pytest" (`test_app_banners`, `test_clinical_data`, `test_config`,
  etc.).
- This is an **environment-setup issue, not a code defect**: Thonny's
  bundled Python does not have `pytest` (or the other dev
  dependencies) installed. Fixed by installing the dev requirements
  into Thonny's Python — Tools → Manage packages, or
  `pip install -r requirements-dev.txt`. Recorded so the setup step
  is not forgotten.
