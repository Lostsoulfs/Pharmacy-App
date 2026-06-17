# 0013 - Red-flag item metadata

## Context

`RED_FLAGS` powers safety and diversion quiz training. The current scenario,
answer, and rationale text must remain visibly unverified until item-level
source evidence and qualified signoff exist.

## Decision

Add item-level review metadata in `pharmacy_app/source_registry.py` for every
current red-flag quiz question. Keep the runtime list rows unchanged and keep
every item status `UNVERIFIED`.

## Consequences

- Future red-flag review PRs have stable per-question metadata to update.
- The app-facing quiz row shape and quiz behavior do not change.
- Source IDs remain review routes only; they do not validate scenario text.
- `DATA_VERIFIED["red_flags"]` remains `False`.

## Confirmation

Required confirmation:

```bash
pytest tests/test_source_registry.py -q
python -m compileall -q pharmacy_app tests tools
pytest -q
```

Evidence level: IMPLEMENTED_UNVERIFIED until local and CI checks pass.
