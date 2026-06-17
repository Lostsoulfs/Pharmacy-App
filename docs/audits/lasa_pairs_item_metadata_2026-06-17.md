# LASA_PAIRS Item Metadata - 2026-06-17

## Scope

Dataset: `LASA_PAIRS` in `pharmacy_app/clinical_data.py`.

This audit artifact records item-level review metadata only. It does not
validate, correct, expand, or remove any LASA question, answer, or rationale.
Every item remains `UNVERIFIED`.

## Current Item Status

Every current LASA question is mapped in
`pharmacy_app/source_registry.py::LASA_PAIR_ITEM_REVIEWS`.

| Review status | Candidate source IDs | Item reviewed on | Pharmacist signoff |
| --- | --- | --- | --- |
| UNVERIFIED | SRC-PTCB-2026-PTCE, SRC-PTCB-2026-KNOWLEDGE | None | None |

Covered questions:

- Look-Alike: Hydroxyzine vs Hydralazine. Which is for Itching?
- Sound-Alike: Humalog vs Humulin. Which is rapid-acting?
- Look-Alike: Zyrtec vs Zyprexa. Which is for allergies?
- Look-Alike: Celebrex vs Celexa. Which treats arthritis pain?
- Sound-Alike: Klonopin vs Clonidine. Which treats seizures and anxiety?
- Look-Alike: Lamictal vs Lamisil. Which treats seizures?
- Sound-Alike: Tramadol vs Trazodone. Which is a pain reliever?
- Sound-Alike: Bupropion vs Buspirone. Which is used for smoking cessation?
- Sound-Alike: Novolog vs Novolin. Which is rapid-acting?
- Look-Alike: Lantus vs Latuda. Which is a long-acting insulin?
- Look-Alike: Plavix vs Paxil. Which is a blood thinner?
- Sound-Alike: Zantac vs Xanax. Which treats heartburn?
- Look-Alike: Diflucan vs Diprivan. Which is an antifungal?
- Sound-Alike: Cyclobenzaprine vs Cyproheptadine. Which is a muscle relaxant?

## Boundary

- No `LASA_PAIRS` question text, answer text, or rationale text was changed.
- No quiz behavior was changed.
- No `DATA_VERIFIED` value was changed.
- Source IDs are candidate review routes, not item-level proof.
- A future qualified review must cite exact source evidence per pair before
  any status can move beyond `UNVERIFIED`.

## Follow-Up

The next LASA PR should review one pair or closely related group at a time
against current qualified training sources and preserve training-only framing.
