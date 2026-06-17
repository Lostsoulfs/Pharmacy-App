# SIG_ABBREVIATIONS Item Metadata - 2026-06-17

## Scope

Dataset: `SIG_ABBREVIATIONS` in `pharmacy_app/clinical_data.py`.

This audit artifact records item-level review metadata only. It does not
validate, correct, expand, or remove any abbreviation meaning. Every item
remains `UNVERIFIED`.

## Current Item Status

Every current abbreviation key is mapped in
`pharmacy_app/source_registry.py::SIG_ABBREVIATION_ITEM_REVIEWS`.

| Review status | Candidate source IDs | Item reviewed on | Pharmacist signoff |
| --- | --- | --- | --- |
| UNVERIFIED | SRC-PTCB-2026-PTCE, SRC-PTCB-2026-KNOWLEDGE | None | None |

Covered keys:

`QD`, `QDAY`, `BID`, `TID`, `QID`, `QHS`, `QAM`, `QPM`, `PRN`, `PO`, `SL`,
`TOP`, `OU`, `OD`, `OS`, `AU`, `AD`, `AS`, `AC`, `PC`, `Q4H`, `Q6H`, `Q8H`,
`Q12H`, `UD`, `AAA`, `NTE`.

## Boundary

- No `SIG_ABBREVIATIONS` meaning text was changed.
- No SIG decoder behavior was changed.
- No `DATA_VERIFIED` value was changed.
- Source IDs are candidate review routes, not item-level proof.
- A future qualified review must cite exact source evidence per abbreviation
  before any status can move beyond `UNVERIFIED`.

## Follow-Up

The next SIG PR should review one abbreviation group at a time against current
qualified training sources and preserve training-only framing.
