# COMMON_RX_FLAGS Item Metadata - 2026-06-17

## Scope

Dataset: `COMMON_RX_FLAGS` in `pharmacy_app/clinical_data.py`.

This audit artifact records item-level review metadata only. It does not
validate, correct, expand, or remove any warning text. Every item remains
`UNVERIFIED`.

## Current Item Status

| Drug key | Review status | Candidate source IDs | Item reviewed on | Pharmacist signoff |
| --- | --- | --- | --- | --- |
| warfarin | UNVERIFIED | SRC-FDA-DRUG-SAFETY, SRC-PTCB-2026-PTCE | None | None |
| methotrexate | UNVERIFIED | SRC-FDA-DRUG-SAFETY, SRC-PTCB-2026-PTCE | None | None |
| insulin | UNVERIFIED | SRC-FDA-DRUG-SAFETY, SRC-PTCB-2026-PTCE | None | None |
| levothyroxine | UNVERIFIED | SRC-FDA-DRUG-SAFETY, SRC-PTCB-2026-PTCE | None | None |
| tramadol | UNVERIFIED | SRC-FDA-DRUG-SAFETY, SRC-DEA-PHARMACIST-MANUAL, SRC-PTCB-2026-PTCE | None | None |
| alprazolam | UNVERIFIED | SRC-FDA-DRUG-SAFETY, SRC-DEA-PHARMACIST-MANUAL, SRC-PTCB-2026-PTCE | None | None |
| amoxicillin | UNVERIFIED | SRC-FDA-DRUG-SAFETY, SRC-PTCB-2026-PTCE | None | None |

## Boundary

- No `COMMON_RX_FLAGS` warning text was changed.
- No app lookup behavior was changed.
- No `DATA_VERIFIED` value was changed.
- Source IDs are candidate review routes, not item-level proof.
- A future qualified review must cite exact source evidence per item before any
  status can move beyond `UNVERIFIED`.

## Follow-Up

The next common-flags PR should review one warning at a time against current
official sources and preserve the training-only pharmacist-review framing.
