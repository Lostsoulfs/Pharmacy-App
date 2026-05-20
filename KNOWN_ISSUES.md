# Known Tool Issues

Dated findings, so you don't re-discover them. Re-verify before
relying on any entry — tooling moves.

## mutmut 3.5.0 — multiprocessing crash
- **Verified:** 2026-05-20
- **Symptom:** `RuntimeError: context has already been set`, raised
  from `mutmut/__main__.py:1152` (`set_start_method('fork')`). It
  fails during mutmut's baseline run, on the first function it
  instruments — so *no* mutation testing runs.
- **Cause:** mutmut calls `set_start_method('fork')` at import time
  with no `force=True`. If a multiprocessing context is already set
  (by pytest, coverage, or the test process), Python raises.
- **Workarounds, best first:**
  1. Pin `mutmut>=3.0,<3.5` — the 3.4.x line predates the regression.
  2. Switch engine: `mutatest` runs mutation trials without modifying
     source files and is pure-pytest — the least-friction alternative
     when mutmut won't start at all.
  3. Run a second mutation engine (`cosmic-ray`) and cross-check
     which mutants each kills; disagreement is a real test gap.
  4. Patch the installed file to `set_start_method('fork',
     force=True)` — fragile, lost on every reinstall.
- **Re-check:** watch for a mutmut release later than 3.5.0 that adds
  `force=True`; then unpin.

## Ephemeral build containers — uncommitted work is lost
- **Verified:** 2026-05-20
- **Note:** cloud/CI build containers are reclaimed after the session.
  Anything not committed and pushed is gone. Commit early; don't leave
  generated artifacts (kits, reports) only on disk.

## Re-verify cadence
- Tool versions / tool bugs: every ~1-2 months.
- External API facts: per that API's own release cycle.
- Math / scientific formulas: effectively never — verify once, cite.
