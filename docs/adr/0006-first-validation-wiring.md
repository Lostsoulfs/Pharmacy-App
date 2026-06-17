# 0006 - First validation wiring boundary

## Context

ADR 0005 added pure validation helpers before UI wiring. The next step is to
use those helpers in app handlers while keeping the first UI-facing change
small enough to review and test without a display.

## Decision

Wire validators into non-visual handler methods first:

- inventory add,
- audit and inventory filters,
- partial-fill add,
- SIG decode callback validation,
- lookup query validation.

Add method-level tests for handlers that can run without a Tk root by
monkeypatching message boxes and database calls. Keep widget-level SIG and
lookup callback smoke tests for a later UI-test PR.

## Consequences

- Inline duplicate validation starts moving out of `app.py`.
- Invalid inventory, filter, partial-fill, SIG, and lookup input has one
  shared validation policy.
- Visible UI behavior changes are intentionally limited to validation errors
  and clearer SIG unknown-token wording.
- Desktop/Pydroid smoke testing is still required for later panel layout and
  interaction changes.

## Confirmation

Required confirmation:

```bash
pytest tests/test_app_validation_wiring.py tests/test_validation.py -q
python -m compileall -q pharmacy_app tests tools
pytest -q
```

Evidence level: IMPLEMENTED_UNVERIFIED until local and CI checks pass.
