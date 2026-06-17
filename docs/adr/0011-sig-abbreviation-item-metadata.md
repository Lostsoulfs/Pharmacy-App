# 0011 - SIG abbreviation item metadata

## Context

`SIG_ABBREVIATIONS` powers the training-only SIG decoder. The current meanings
must remain visibly unverified until item-level source evidence and qualified
signoff exist.

## Decision

Add item-level review metadata in `pharmacy_app/source_registry.py` for every
current SIG abbreviation key. Keep the runtime dictionary unchanged and keep
every item status `UNVERIFIED`.

## Consequences

- Future SIG review PRs have stable per-item metadata to update.
- The app-facing dictionary shape and decoder behavior do not change.
- Source IDs remain review routes only; they do not validate meaning text.
- `DATA_VERIFIED["sig_abbreviations"]` remains `False`.

## Confirmation

Required confirmation:

```bash
pytest tests/test_source_registry.py -q
python -m compileall -q pharmacy_app tests tools
pytest -q
```

Evidence level: IMPLEMENTED_UNVERIFIED until local and CI checks pass.
