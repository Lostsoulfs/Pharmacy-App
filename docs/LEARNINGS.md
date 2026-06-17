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

## 2026-06-17 - First validation wiring

- Wire non-visual handler methods through validators before broader layout
  changes. Inventory, filters, and partial fills can be tested without a Tk
  root by monkeypatching messagebox and DB calls.
- Keep SIG and lookup callback tests at the pure-helper layer until a dedicated
  UI smoke-test path exists for widget-level callbacks.

## 2026-06-17 - Partial-fill edit path

- Update only unresolved partial-fill rows. If a save races with resolve/delete
  state, clear edit mode and show the stale-row message instead of rewriting
  ledger history.
- Keep edit-path tests split across persistence helpers and Tk-free handler
  methods. Full widget/touch smoke should stay in a later UI test PR.

## 2026-06-17 - Scroll input hardening

- Treat `bind_all` scroll handlers as global state. Every sequence added by a
  scrollable panel must also be removed when the view changes.
- Keyboard scrolling should skip Entry/Text-style widgets so navigation keys
  keep their normal meaning while the user is typing.

## 2026-06-17 - Admin filter status

- Long admin pages need filter state near the top, not only inside the section
  where the filter is applied.
- Export buttons should say when they ignore the current view filter so the
  user does not mistake a filtered preview for a filtered export.

## 2026-06-17 - Common RX flag metadata

- For content domains, item-level metadata can advance review readiness without
  changing clinical facts. Keep row shape stable and mark each item unverified
  until exact source evidence and pharmacist signoff exist.

## 2026-06-17 - SIG abbreviation metadata

- For compact dictionary datasets, keep an explicit metadata key list so future
  data additions fail tests until review metadata is added.

## 2026-06-17 - LASA pair metadata

- For quiz-list datasets, use the current question text as the item metadata
  key so wording additions or rewrites fail tests until review metadata is
  updated.
