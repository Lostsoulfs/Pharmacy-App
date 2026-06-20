# Backlog — Pharmacy-App

A running parking lot for deferred work, known gaps, and out-of-scope items, so the working repo
stays clean and nothing gets lost. Not a roadmap or a promise. Add items as
`- [ ] <item> — <why deferred / owner / status>`. Tool gotchas live in
[`KNOWN_ISSUES.md`](../KNOWN_ISSUES.md); the running history in [`docs/LEARNINGS.md`](LEARNINGS.md);
audit detail in [`docs/audits/`](audits/).

## Blocked on a human (pharmacist sign-off)

- [ ] **Clinical/law dataset sign-off (Nathan).** Automated audits complete (2026-05-20); per
  ADR-C05 the `DATA_VERIFIED` keys stay `False` until the pharmacist confirms. Until then the app
  presents this content as **unverified training material** only. Owner: Nathan.

## Known gaps (from the 2026-05-21 code audit — fixes deferred, no code changed)

- [ ] **`app.py` UI is 0%-covered** (846 untested statements, monolithic Tkinter). Needs either a
  live Pydroid/desktop manual pass or a headless harness extracting testable seams from the UI.
- [ ] **4 medium + 8 low code-audit findings** recorded but not yet fixed — see
  `docs/audits/code_audit_2026-05-21.md` sections 3–4.
- [ ] **215 surviving mutants** on `logic.py` (630 total, 415 killed) — strengthen tests where the
  surviving mutants reveal weak assertions.
- [ ] **291 ruff E/W style-debt errors** (pre-existing; 0 pyflakes `F`). Cosmetic; clear when
  convenient, not urgent.

## Decision-gated

- [ ] **Clinical-calculator-as-agent-skill — DEFERRED.** `pharmacy_app/logic.py` exposes pure,
  deterministic calculators (insulin/days-supply, DEA checksum, CrCl, BSA, pediatric dosing) that
  *could* be published as an A2A/MCP skill, but advertising dosing/clinical math as a callable
  capability reads as a medical/clinical claim. **Not doing this** until (a) pharmacist sign-off and
  (b) an explicit med-safety-claim review. Logged so the option isn't lost.

## Cross-repo / org

- [ ] **Dedicated logging repo (org-wide idea).** Scott wants a single repo just for logs/history
  later, to keep app repos clean. Out of scope here; logged so it isn't lost.
