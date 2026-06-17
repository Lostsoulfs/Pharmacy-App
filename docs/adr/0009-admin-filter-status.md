# 0009 - Admin filter status and clear-all action

## Context

The Admin panel had separate filters for inventory and audit log sections. Each
section could clear itself, but an active filter could still be easy to miss
while scrolling a long admin page.

## Decision

Add a compact active-filter status at the top of Admin when either filter is
set. The status lists active audit and inventory filters and offers one
`Clear All Filters` action. Keep the existing section-level filter and clear
buttons. Add short helper text clarifying that:

- inventory filtering matches drug names only,
- audit filtering matches user names and action text,
- audit export still writes the full audit log.

## Consequences

- Admin users can see filtered state before scanning section contents.
- Filter clearing can be done from one predictable place.
- Export behavior is clearer without changing exported data.
- This PR changes Admin UI flow only; it does not alter clinical/legal data,
  source metadata, schema, or runtime dependencies.

## Confirmation

Required confirmation:

```bash
pytest tests/test_app_validation_wiring.py -q
python -m compileall -q pharmacy_app tests tools
pytest -q
```

Evidence level: IMPLEMENTED_UNVERIFIED until local and CI checks pass.
