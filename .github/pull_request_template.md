## What & why

What changed, and why?

## Changes

-

## Deviations from plan

None.

## AI assistance

- [ ] No AI-assisted changes
- [ ] AI-assisted changes present (areas listed below)

## Clinical / data risk

- [ ] Docs or tooling only
- [ ] Logic (calculators, DEA check, matching)
- [ ] Clinical or law data (`DATA_VERIFIED` implications — ADR-C05)
- [ ] DB schema (additive `ALTER TABLE` only — ADR-C01)
- [ ] UI (needs desktop/Pydroid layout check; CI smoke is not phone proof)
- [ ] Dependency or CI

## Source boundary

- [ ] No clinical, law, vaccine, medication, or TPR facts changed
- [ ] Source IDs added/updated in `docs/OFFICIAL_SOURCES_2026.md` or `docs/DATA_SOURCE_REGISTER_2026.md`
- [ ] Qualified pharmacist signoff included before any `DATA_VERIFIED` date change
- [ ] State-specific law not changed, or state track is identified here:

## Verification

- [ ] `pytest -q` green
- [ ] No new ruff `F` errors
- [ ] On-device check done, if UI changed
- [ ] No clinical facts invented; sources cited where data changed
- [ ] Repository controls checked, if governance files changed

## Records

- [ ] ADR added/updated, if this changes durable rules or architecture
- [ ] `docs/LEARNINGS.md` added/updated, if this records a gotcha or rule change

Commands run:

```text

```
