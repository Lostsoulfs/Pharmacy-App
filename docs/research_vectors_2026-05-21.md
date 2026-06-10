# Research — Update Vectors for Gap Closure

- **Date:** 2026-05-21
- **Researcher:** Claude Code (`claude-opus-4-7`)
- **Scope:** web research on three vectors — tooling currency, an
  `app.py` test-coverage technique, and code modernization — to
  inform the fix backlog in `docs/audits/code_audit_2026-05-21.md`.
- **Constraint:** research only. NO code or config was changed; this
  document is the sole deliverable. Findings feed a later session.

## 1. Tooling currency

| Tool | Project pin | Latest (May 2026) | Verdict |
|------|-------------|-------------------|---------|
| mutmut | `>=3.0,<3.5` | **3.5.0** (2026-02-22) | Pin stays — see below |
| ruff | `>=0.15` | 0.15.x (2026-05-14) | Current |
| pytest | `>=9.0` | 9.0.3 (2026-04-07) | Current |

**mutmut — the `KNOWN_ISSUES.md` re-check item is resolved (negative).**
3.5.0 (released 2026-02-22) is still the latest version; nothing has
shipped after it. The project changelog (`HISTORY.rst`) shows **no
fix** for `set_start_method` / multiprocessing-context / `fork` — the
only process-related change pending is an unrelated `use_setproctitle`
option. So the `set_start_method('fork')` bug is **still unfixed
upstream**. Action: the `requirements-dev.txt` pin `mutmut<3.5` stays;
`KNOWN_ISSUES.md`'s "watch for a release later than 3.5.0" note can be
annotated "re-checked 2026-05-21 — still no fix" in a later session.

**ruff** — latest (May 2026) ships **block suppression comments**
(`# ruff: disable[rule]` / `# ruff: enable[rule]`). This is directly
useful for audit finding **M4**: the 291 pre-existing E/W errors could
be fenced off in blocks (or per-file-ignored) so `nox -s lint` goes
green without a wholesale style rewrite. The `>=0.15` pin already
allows this.

**pytest / hypothesis / mypy / nox** — the pins are all current; no
breaking-change migration is owed. pytest 9.0.x added
`strict_parametrization_ids` (minor, opt-in).

## 2. `app.py` test technique — the 0% coverage gap

The audit's largest gap is `app.py` at 0% coverage (846 statements),
on the assumption that "Tkinter cannot run in CI" (`CLAUDE.md`).
Research **partially overturns that assumption.**

A headless Tkinter test needs **two** things:
1. **A virtual display** — `Xvfb` + the `pytest-xvfb` plugin. The
   plugin auto-runs the suite under Xvfb so `Tk()` finds a display.
2. **The `tkinter` module itself** — the `python3-tk` system package.

Container check (2026-05-21):
- `Xvfb` and `xvfb-run` **are installed** here (`/usr/bin/Xvfb`).
- `tkinter` is **not** importable (`python3-tk` not installed).

So the blocker in *this* container is the missing module, not the
display. Implications:
- **GitHub Actions CI: a real `app.py` smoke test IS feasible.** CPython
  on GA runners ships `tkinter`, and Xvfb is available. Adding
  `pytest-xvfb` to `requirements-dev.txt` would let a test
  instantiate `PharmacyApp`, drive `navigate_to` through every panel,
  and assert no exception — turning today's static AST check
  (`test_app_banners.py`) into actual executable coverage.
- **This Claude container:** the same test would need a one-line
  `apt-get install python3-tk`; it is ephemeral, so not a durable fix.
- **Still not CI-testable:** actual rendering, layout, touch-scroll,
  and Pydroid behavior. The `CLAUDE.md` "on-device check" requirement
  remains correct for *those* — but "Tkinter cannot run in CI" is too
  strong; a build/smoke test can.

Recommendation for a later session: add `pytest-xvfb`, write a panel
smoke test guarded by `pytest.importorskip("tkinter")` so it executes
in CI and skips cleanly where the module is absent. This is the single
highest-leverage coverage win and complements audit finding **M1**
(extracting panel SQL into testable `data.py` helpers).

## 3. Code modernization

**Type annotations.** The code is entirely unannotated, yet
`noxfile.py` runs a `types` session (`mypy pharmacy_app`) — which
currently passes *vacuously* because there is nothing to check.
Current (2026) gradual-typing guidance:
- Do **not** start with `mypy --strict` — annotate module-by-module.
- Type the most logic-critical, bug-prone code first. Here that is
  `logic.py` — pure functions, already 90% covered, no Tk/DB imports,
  the natural first target. `data.py` next, `app.py` last.
- Use built-in syntax (`X | None`, `list[str]`) — the `py311` target
  supports it; no `typing` imports needed.
- `MonkeyType` can auto-generate a first pass of annotations from a
  test run.
Recommendation: a later session annotates `logic.py` and turns on
mypy strictness for that module only — making the `types` session
actually meaningful without a codebase-wide commitment.

**Lint debt (ties to M4).** The 291 ruff errors are all E/W style
(0 pyflakes `F`). Options, in order of preference: (a) `ruff format`
the codebase once to clear the bulk of E/W mechanically, then commit
the reformat separately; (b) baseline the remainder with per-file
ignores or the new block-suppression comments. Either makes
`nox -s lint` green and restores the default `nox` as a usable gate.

## 4. Update vectors mapped to audit findings

| Vector | Closes / supports | Effort |
|--------|-------------------|--------|
| `pytest-xvfb` + guarded panel smoke test | `app.py` 0% coverage; complements M1 | Medium |
| `ruff format` + block-suppression / per-file-ignore | M4 (`nox -s lint` red) | Low |
| Annotate `logic.py`, scope mypy strict to it | Makes the `types` session real | Medium |
| Annotate the mutmut re-check note | `KNOWN_ISSUES.md` housekeeping | Trivial |

None of these require new external dependencies beyond `pytest-xvfb`.
All are deferred to a later session per the research-only scope.

## Sources

- [mutmut · PyPI](https://pypi.org/project/mutmut/)
- [mutmut HISTORY.rst](https://github.com/boxed/mutmut/blob/main/HISTORY.rst)
- [Ruff v0.15.0 / changelog](https://astral.sh/blog/ruff-v0.15.0)
- [ruff CHANGELOG.md](https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md)
- [pytest 9.0.0 release notes](https://docs.pytest.org/en/stable/announce/release-9.0.0.html)
- [pytest · PyPI](https://pypi.org/project/pytest/)
- [pytest-xvfb · PyPI](https://pypi.org/project/pytest-xvfb/)
- [pytest-xvfb (GitHub)](https://github.com/The-Compiler/pytest-xvfb)
- [Running Tkinter in test — GitHub community discussion](https://github.com/orgs/community/discussions/62479)
- [xvfbwrapper (GitHub)](https://github.com/cgoldberg/xvfbwrapper)
- [Python Type Hints and mypy (2026)](https://tutorials.technology/tutorials/python-type-hints-mypy-2026.html)
- [mypy documentation](https://mypy.readthedocs.io/)
