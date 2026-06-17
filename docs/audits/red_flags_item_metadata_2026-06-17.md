# RED_FLAGS Item Metadata - 2026-06-17

## Scope

Dataset: `RED_FLAGS` in `pharmacy_app/clinical_data.py`.

This audit artifact records item-level review metadata only. It does not
validate, correct, expand, or remove any red-flag scenario, answer, or
rationale. Every item remains `UNVERIFIED`.

## Current Item Status

Every current red-flag question is mapped in
`pharmacy_app/source_registry.py::RED_FLAG_ITEM_REVIEWS`.

| Review status | Candidate source IDs | Item reviewed on | Pharmacist signoff |
| --- | --- | --- | --- |
| UNVERIFIED | SRC-PTCB-2026-PTCE, SRC-FDA-DRUG-SAFETY, SRC-DEA-PHARMACIST-MANUAL | None | None |

Covered questions:

- Patient picking up Warfarin and Advil (Ibuprofen)?
- C-II Codeine syrup from out-of-state dentist?
- Cash price for 90-day supply of Oxycodone?
- Methotrexate written for once-daily dosing?
- Patient with a documented penicillin allergy handed Amoxicillin?
- Patient on Sildenafil also picking up Nitroglycerin?
- Controlled-substance scripts from several different prescribers in a short window?
- SSRI antidepressant filled alongside Tramadol?
- Adult-strength dose on a prescription for a small child?
- Patient buying large or repeated quantities of pseudoephedrine?
- ACE inhibitor (e.g. Lisinopril) with a potassium supplement?
- Isotretinoin presented by a patient who may be pregnant?
- Opioid prescription presented well before the previous fill should have run out?
- Aspirin on a prescription for a child with a viral illness?

## Boundary

- No `RED_FLAGS` question text, answer text, or rationale text was changed.
- No quiz behavior was changed.
- No `DATA_VERIFIED` value was changed.
- Source IDs are candidate review routes, not item-level proof.
- A future qualified review must cite exact source evidence per scenario
  before any status can move beyond `UNVERIFIED`.

## Follow-Up

The next red-flag PR should review one safety or controlled-substance scenario
at a time against current qualified sources and preserve training-only framing.
