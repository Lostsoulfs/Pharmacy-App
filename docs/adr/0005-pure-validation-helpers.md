# 0005 - Pure validation helpers before Tkinter wiring

## Context

The app-flow hardening plan includes input length caps, SIG junk rejection,
clearer lookup behavior, safer partial-fill handling, and clearer admin/audit
flows. The current Tkinter handlers contain inline validation logic mixed with
message boxes and database calls.

Changing UI handlers before a pure validation layer exists would make behavior
harder to test and harder to review on desktop and Pydroid.

## Decision

Add `pharmacy_app/validation.py` with pure helpers for:

- bounded text fields,
- optional filters,
- drug and patient names,
- strict zero-padded ISO dates,
- positive integer quantities,
- lookup query text,
- SIG token normalization and junk-character rejection,
- inventory and partial-fill payload validation.

Do not wire Tkinter handlers through these helpers in this PR. That wiring
comes later as small UI smoke-tested PRs.

## Consequences

- Validation behavior is testable without tkinter or SQLite.
- Later UI PRs can replace inline validation with helper calls one panel at a
  time.
- No visible app behavior changes until handlers are explicitly wired.

## Confirmation

Required confirmation:

```bash
pytest tests/test_validation.py -q
python -m compileall -q pharmacy_app tests tools
pytest -q
```

Evidence level: IMPLEMENTED_UNVERIFIED until local and CI checks pass.
