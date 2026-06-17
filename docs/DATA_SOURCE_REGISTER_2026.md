# Data Source Register

Reviewed June 17, 2026.

This register maps current `config.DATA_VERIFIED` dataset keys to candidate
source families and PTCE domains. It is review-routing metadata only. It does
not validate the bundled data, does not change app behavior, and does not allow
any `DATA_VERIFIED` key to be flipped.

Machine-readable companion metadata lives in
`pharmacy_app/source_registry.py`. That registry mirrors this document at the
dataset level only; it is not item-level verification and cannot clear any
UNVERIFIED banner.

## Dataset Domains

| Dataset key | Current status | App area | Candidate source IDs | PTCE domain mapping | Next review action |
| --- | --- | --- | --- | --- | --- |
| `brand_generic` | UNVERIFIED | Quiz training, drug lookup | SRC-PTCB-2026-PTCE, SRC-PTCB-2026-KNOWLEDGE | Medications | Map each brand/generic/class row to source-backed training scope before any content correction. |
| `red_flags` | UNVERIFIED | Quiz training, safety prompts | SRC-PTCB-2026-PTCE, SRC-FDA-DRUG-SAFETY, SRC-DEA-PHARMACIST-MANUAL | Medications; Patient Safety and Quality Assurance; Federal Requirements | Review one warning scenario at a time and separate federal controlled-substance issues from general safety issues. |
| `lasa_pairs` | UNVERIFIED | Quiz training | SRC-PTCB-2026-PTCE, SRC-PTCB-2026-KNOWLEDGE | Patient Safety and Quality Assurance; Medications | Item-level metadata added in `docs/audits/lasa_pairs_item_metadata_2026-06-17.md`; pair text still needs qualified review. |
| `sig_abbreviations` | UNVERIFIED | SIG decoder | SRC-PTCB-2026-PTCE, SRC-PTCB-2026-KNOWLEDGE | Order Entry and Processing | Item-level metadata added in `docs/audits/sig_abbreviations_item_metadata_2026-06-17.md`; meaning text still needs qualified review. |
| `common_rx_flags` | UNVERIFIED | Drug lookup, warning notes | SRC-PTCB-2026-PTCE, SRC-FDA-DRUG-SAFETY | Medications; Patient Safety and Quality Assurance | Item-level metadata added in `docs/audits/common_rx_flags_item_metadata_2026-06-17.md`; warning text still needs qualified review. |
| `vaccines` | UNVERIFIED | Vaccine eligibility panel | SRC-CDC-VACCINE-SCHEDULES, SRC-PTCB-2026-PTCE | Medications; Federal Requirements where applicable | Rebuild vaccine entries from current provider schedules in a dedicated PR. |
| `law` | UNVERIFIED | Law panel | SRC-DEA-PHARMACIST-MANUAL, SRC-DEA-CSA, SRC-PTCB-2026-PTCE | Federal Requirements | Keep federal law separate from state law. Add Tennessee or another state only after a state-specific track is approved. |
| `tpr` | UNVERIFIED | TPR insurance guide | SRC-PTCB-2026-PTCE, SRC-PTCB-2026-KNOWLEDGE | Order Entry and Processing; Patient Safety and Quality Assurance | Treat as workflow training. Do not claim payer-specific correctness without qualified review. |

## Review States

- `UNVERIFIED`: current state for every dataset key. App warnings must remain.
- `SOURCE_MAPPED`: every item has at least one source ID and review date, but no
  pharmacist signoff yet.
- `PHARMACIST_SIGNED`: a qualified pharmacist signed the dated audit artifact.
  Only this state can support a `DATA_VERIFIED` date change.

## Code Registry Requirements

- Registry keys must match `config.DATA_VERIFIED` exactly.
- Current registry status remains `UNVERIFIED` for every dataset key.
- Source IDs are candidate review routes, not item-level proof.
- PTCE domain mappings use the four 2026 outline domains: Medications,
  Federal Requirements, Patient Safety and Quality Assurance, and Order Entry
  and Processing.
- `DATA_VERIFIED` remains the UI source of truth.

## Required Evidence For Future Content PRs

- Source ID and URL from `docs/OFFICIAL_SOURCES_2026.md`.
- Review date.
- Reviewer role or explicit `unqualified review` label.
- Item-level change summary.
- Tests run after the change.
- Explicit statement that unchanged items remain unverified.
