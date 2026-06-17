# 0007 - Partial-fill edit path

## Context

The partial-fill ledger allowed adding and resolving open rows, but not editing
an entry after a typo. That pushed users toward resolving and recreating rows,
which is noisy and makes the audit trail harder to read.

## Decision

Add an edit path for unresolved partial-fill rows only:

- show an Edit action beside each open partial,
- reuse the existing partial-fill validation helper before saving,
- add a data helper that updates only `resolved=0` rows,
- audit-log successful edits,
- clear edit mode when the row is stale, already resolved, or missing.

Resolved rows remain immutable through this UI path.

## Consequences

- Typo fixes no longer require creating replacement ledger rows.
- Stale edit attempts do not rewrite resolved ledger history.
- This PR changes partial-fill workflow only; it does not change clinical or
  legal content, source metadata, SQLite schema, or verification status.
- Widget-level and touch smoke testing remain deferred to broader UI PRs.

## Confirmation

Required confirmation:

```bash
pytest tests/test_data.py tests/test_app_validation_wiring.py -q
python -m compileall -q pharmacy_app tests tools
pytest -q
```

Evidence level: IMPLEMENTED_UNVERIFIED until local and CI checks pass.
