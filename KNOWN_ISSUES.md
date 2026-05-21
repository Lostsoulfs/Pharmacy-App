# Known Tool Issues

Dated findings, so you don't re-discover them. Re-verify before
relying on any entry — tooling moves.

## mutmut 3.5.0 — `set_start_method` crash under a pre-set context
- **Verified:** 2026-05-21 (re-verified; impact corrected)
- **Symptom:** `RuntimeError: context has already been set`, raised
  from `mutmut/__main__.py:1152` (`set_start_method('fork')`) at
  import time.
- **When it bites:** only when mutmut's `__main__` is imported into a
  process that has *already* called `set_start_method` — e.g.
  `coverage run -m mutmut`, or `import mutmut` from inside a pytest
  run.
- **When it does NOT bite:** the normal `mutmut run` CLI and
  `nox -s mutation` (`noxfile.py:61`) launch a fresh process with no
  pre-set context, so `set_start_method('fork')` succeeds. Re-verified
  2026-05-21: a full `mutmut run` completed (630 mutants, ~27 s, no
  crash). The earlier "no mutation testing runs" note was wrong for
  this path — Layer 4 works via the standard invocation.
- **Cause:** mutmut calls `set_start_method('fork')` at module scope
  with no `force=True`; the latest release is still 3.5.0, unfixed.
- **Do:** run mutation testing via `mutmut run` / `nox -s mutation`.
- **Don't:** invoke mutmut as `coverage run -m mutmut`, or import it
  from inside a test process.
- **If you still hit it:** `requirements-dev.txt` pins
  `mutmut>=3.0,<3.5`; the 3.4.x line predates the regression. Other
  options: `mutatest` (pure-pytest, no source edits) or patching the
  installed line to `set_start_method('fork', force=True)` (fragile,
  lost on every reinstall).
- **Re-check:** watch for a mutmut release later than 3.5.0 that adds
  `force=True`; then the pin can be dropped.

## Ephemeral build containers — uncommitted work is lost
- **Verified:** 2026-05-20
- **Note:** cloud/CI build containers are reclaimed after the session.
  Anything not committed and pushed is gone. Commit early; don't leave
  generated artifacts (kits, reports) only on disk.

## Re-verify cadence
- Tool versions / tool bugs: every ~1-2 months.
- External API facts: per that API's own release cycle.
- Math / scientific formulas: effectively never — verify once, cite.
