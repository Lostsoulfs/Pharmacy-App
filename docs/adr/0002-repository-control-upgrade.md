# 0002 - Repository-control upgrade for Pharmacy-App

## Context

The repo already has branch discipline, security scanning, pinned workflow
actions, a control policy, and a structural control audit. The full upgrade
campaign needs those controls to also cover the new source-boundary and ADR
records so future rule work cannot remove them silently.

## Decision

Extend `.github/control-policy.json` so the control audit requires:

- `docs/OFFICIAL_SOURCES_2026.md`
- `docs/DATA_SOURCE_REGISTER_2026.md`
- `docs/LEARNINGS.md`
- `docs/adr/README.md`

The audit remains structural. It checks that required governance files and
workflow controls exist; it does not prove clinical safety, HIPAA compliance,
de-identification, branch protection settings, or pharmacist review.

## Consequences

- Source-boundary and learning records become part of the repo's required
  governance surface.
- Future PRs that delete or empty those records should fail the repository
  control audit.
- Actual GitHub settings, branch protection, and dataset review still need
  separate confirmation.

## Confirmation

Required confirmation:

```bash
python tools/control_audit.py
```

Evidence level: IMPLEMENTED_UNVERIFIED until local and CI checks pass.
