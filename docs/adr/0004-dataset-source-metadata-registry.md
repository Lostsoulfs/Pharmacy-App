# 0004 - Dataset source metadata registry

## Context

The app has bundled training datasets for medications, safety prompts, SIG
abbreviations, vaccines, law notes, and TPR guidance. The current rows must
stay unchanged until each content domain receives qualified review, but future
content PRs need a stable place to record source IDs, PTCE domains, and review
status.

Adding source fields directly to every runtime row would change the app-facing
data shape before the UI and tests are prepared for it.

## Decision

Add `pharmacy_app/source_registry.py` as a companion metadata registry. It
records, per `config.DATA_VERIFIED` key:

- review status,
- candidate source IDs,
- PTCE domain mapping,
- source-register review date,
- item review date,
- pharmacist signoff state,
- a scope note that preserves the unverified boundary.

The registry is metadata only. It does not validate current rows and does not
clear any `UNVERIFIED` banner.

## Consequences

- Future data PRs can update one dataset domain at a time with an explicit
  metadata path.
- Existing UI and runtime dataset shapes remain unchanged.
- `DATA_VERIFIED` remains the source of truth for visible verification status.
- A source ID or PTCE domain mapping still does not prove item correctness.

## Confirmation

Required confirmation:

```bash
pytest tests/test_source_registry.py -q
python -m compileall -q pharmacy_app tests tools
pytest -q
```

Evidence level: IMPLEMENTED_UNVERIFIED until local and CI checks pass.
