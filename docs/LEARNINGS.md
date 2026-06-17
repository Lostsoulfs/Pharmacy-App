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

## 2026-06-17 - CI control gate hardening

- CI workflow tool installs should be pinned in the workflow, not left to the
  latest package resolver. `tests.yml` now matches the artifact and release
  workflows by installing `nox==2026.4.10`.
- Write-scoped workflow permissions are allowed only when the control policy
  records the workflow, job, permission, and reason. Top-level workflow
  permissions stay read-only.
- The secret/PII scan depends on a trusted scanner checkout from the base
  branch. The control audit now checks for that checkout plus scanner self-test
  and PR-diff scan commands.

## 2026-06-17 - Dataset source metadata

- Source metadata is now a companion registry, not extra fields on the runtime
  rows. This preserves the existing Tkinter/data call sites while giving future
  content PRs a stable place to record source IDs and PTCE domains.
- Registry entries are dataset-level routing metadata only. They do not
  validate item facts and do not affect the UNVERIFIED banners.
- Comments in `clinical_data.py` should say "automated audit recorded" when
  pharmacist signoff is still pending. Avoid "verified" wording unless
  `DATA_VERIFIED` has a signed date.

## 2026-06-17 - Pure validation before UI wiring

- Add pure validation helpers before changing Tkinter handlers. This lets
  length caps, date checks, SIG token rejection, and partial-fill payload rules
  be tested without desktop/Pydroid UI variability.
- Keep first validation PR behavior-preserving by not wiring panels yet. UI
  wiring can then happen one panel at a time with focused smoke tests.
