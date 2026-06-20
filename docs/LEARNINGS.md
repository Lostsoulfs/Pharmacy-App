# Learnings

Running log of project-level gotchas, decisions, and what was already vetted — so future sessions
don't re-discover or re-litigate it. Append (don't rewrite) with the date. Referenced by `AGENTS.md`
(source-of-truth order #3).

This is the **project** log. Two companions hold detail, don't duplicate them here:

- **Tool gotchas** → [`KNOWN_ISSUES.md`](../KNOWN_ISSUES.md) (e.g. the mutmut 3.5.0 `set_start_method`
  crash and the safe `mutmut run` / `nox -s mutation` invocation).
- **Dated audits** → [`docs/audits/`](audits/) (code, clinical datasets, brand/generic, law/TPR).

## 2026-05-20/21 — first full audit pass

- **Read-only audit discipline pays off.** Every finding was re-confirmed by reading the cited code
  before it was recorded; three survey "findings" were disproved outright as false positives. Survey
  output is a *lead*, not a result. (`docs/audits/code_audit_2026-05-21.md`.)
- **Baseline captured:** 99 tests pass; mutation 630 mutants / 415 killed on `logic.py`; 0
  high-severity defects, 4 medium + 8 low recorded with fixes **deferred** (no code changed in the
  audit). The open findings live in [`docs/BACKLOG.md`](BACKLOG.md).
- **`app.py` is 0%-covered by design** — it is a monolithic Tkinter UI (846 statements) that needs a
  live Pydroid/desktop session; `theme.py` 0% is benign (pure constants). Pure logic is well-covered
  (`logic.py` 90%, `data.py` 96%). The total ~34% figure is dominated by the untestable UI, not by
  weak logic tests.
- **Data integrity gate (ADR-C05):** the clinical/law datasets were automated-cross-checked +
  web-verified (VACCINES vs CDC/ACIP), but the in-code `DATA_VERIFIED` keys **stay `False` until a
  pharmacist (Nathan) signs off.** Unverified content is never presented as verified — this is the
  app's core honesty boundary, restated in the README and `docs/OFFICIAL_SOURCES_2026.md`.

## 2026-06-17 — full repository engineering controls installed

- Adopted the org control stack (PR #7): AGENTS/CLAUDE/SECURITY contract, secret/PII pre-commit + CI
  scanner (public-repo BLOCK policy), `tools/control_audit.py` + `.github/control-policy.json`
  required-files gate, CodeQL, dependency review, OpenSSF scorecard, multi-version test matrix.

## 2026-06-20 — framework alignment (this change)

- Added `STATUS.md` (lifecycle source-of-truth) + this `docs/LEARNINGS.md` — both were already
  referenced by `AGENTS.md`'s source-of-truth order but did not yet exist. Added `docs/BACKLOG.md`.
  No agent-interop surface: the clinical calculators are real and pure, but advertising them as a
  callable skill would read as a clinical/med-safety claim, which is forbidden until pharmacist
  sign-off — logged as decision-gated in the backlog.
