# 0010 - Common RX flag item metadata

## Context

`COMMON_RX_FLAGS` is a small clinical warning dataset used by the drug lookup
panel. The warnings remain useful only as training prompts, and every current
item still needs qualified review before correctness can be claimed.

## Decision

Add item-level review metadata in `pharmacy_app/source_registry.py` for every
current `COMMON_RX_FLAGS` drug key. Keep the runtime tuple rows unchanged and
keep every item status `UNVERIFIED`.

## Consequences

- Future content-review PRs have stable per-item metadata to update.
- The app-facing dataset shape and lookup behavior do not change.
- Source IDs remain review routes only; they do not validate warning text.
- `DATA_VERIFIED["common_rx_flags"]` remains `False`.

## Confirmation

Required confirmation:

```bash
pytest tests/test_source_registry.py -q
python -m compileall -q pharmacy_app tests tools
pytest -q
```

Evidence level: IMPLEMENTED_UNVERIFIED until local and CI checks pass.
