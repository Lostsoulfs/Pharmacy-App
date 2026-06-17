# Learnings

Append dated, evidence-backed findings here when work changes the repo's
rules, tooling, source boundary, verification strategy, or known gotchas.

## 2026-06-17 - Governance foundation

- The first Pharmacy-App upgrade PR is intentionally governance and source
  boundary only. It does not change app logic, Tkinter flow, runtime
  dependencies, clinical content, law content, or `DATA_VERIFIED`.
- `Inbound-health-care/demo-repository` is only a small private demo repo in
  the current GitHub installation. The healthcare governance blueprint loaded
  for this campaign is `Lost-secuirty/Health-Prototype`, not that demo repo.
- Source links in `docs/OFFICIAL_SOURCES_2026.md` are starting points for
  qualified review. A source link or dataset mapping does not validate bundled
  clinical/legal data or justify flipping any `DATA_VERIFIED` key.
- Tooling changed since the May research note: pytest 9.1.0, mypy 2.1, Ruff
  0.15.17, and mutmut 3.6.0 exist as of this recheck. Dependency changes are
  deferred until a toolchain PR can verify them on the intended OS path.
