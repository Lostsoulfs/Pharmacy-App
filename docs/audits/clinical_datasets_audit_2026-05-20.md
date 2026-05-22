# Clinical Datasets Audit — RED_FLAGS, LASA_PAIRS, SIG_ABBREVIATIONS, COMMON_RX_FLAGS, VACCINES

- **Datasets:** the 5 remaining `clinical_data.py` datasets (the Top
  200 `BRAND_GENERIC` list is covered separately in
  `brand_generic_audit_2026-05-20.md`).
- **Audit date:** 2026-05-20
- **Auditor:** Claude Code (automated cross-check + web verification)
- **Status:** PENDING pharmacist sign-off — automated audit complete
  2026-05-20; per ADR-C05 the five `DATA_VERIFIED` keys stay False
  until the pharmacist confirmation below is signed.

## Methodology

Each dataset's clinical content was cross-checked for accuracy and
internal consistency. The VACCINES dataset — the highest-risk, since
immunization schedules change yearly — was additionally web-verified
against the current CDC/ACIP guidance, with focus on the recently
changed adult pneumococcal and RSV age recommendations. This is not
an authoritative reference; the pharmacist should spot-confirm before
relying on it clinically.

## RED_FLAGS (14 entries) — VERIFIED, no changes

Dispensing-safety scenarios. All 14 `rationale` claims are sound and
match standard pharmacy practice: warfarin+NSAID bleeding risk,
methotrexate weekly-dosing fatal error, penicillin/amoxicillin
cross-allergy, PDE5+nitrate hypotension, SSRI+tramadol serotonin
syndrome, ACE inhibitor + potassium hyperkalemia, isotretinoin
teratogenicity / iPLEDGE, aspirin + pediatric viral illness / Reye's
syndrome, and the controlled-substance diversion patterns. No
corrections.

## LASA_PAIRS (14 entries) — VERIFIED, no changes

Look-alike/sound-alike drug pairs. All 14 pairs, answers, and
distinguishing rationales are correct (consistent with ISMP
confused-drug-name pairs). Minor simplification noted, not an error:
the Humalog/Humulin and Novolog/Novolin entries call Humulin/Novolin
"intermediate-acting" — true of the NPH (N) products; the brands also
include short-acting (R) products. Acceptable for a name-confusion
quiz. No corrections.

## SIG_ABBREVIATIONS (27 entries) — VERIFIED, no changes

All 27 abbreviation→meaning mappings are correct. Note: some keys
(QD, QDAY) appear on the ISMP error-prone abbreviation list — but
this is a *decoder*, so carrying them with the correct meaning is
appropriate. No corrections.

## COMMON_RX_FLAGS (7 entries) — VERIFIED, no changes

Drug-lookup overlay advisories for warfarin, methotrexate, insulin,
levothyroxine, tramadol, alprazolam, amoxicillin. All seven flag
texts are sound, conservative, pharmacist-review-oriented advisories.
No corrections.

## VACCINES (13 entries) — VERIFIED, 1 correction applied

Web-verified against the current CDC/ACIP schedule.

| Vaccine | Finding |
|---------|---------|
| RSV | **CORRECTED.** `ages` said "adults 60-74 at increased risk"; ACIP (April 2025, adopted June 2025) expanded the at-risk recommendation down to age 50. Changed to **"adults 50-74 at increased risk"**. |
| Pneumococcal (PCV) | Confirmed — "Adults 50 and older" matches the current CDC recommendation (lowered from 65 in 2024). |
| All others | Influenza, COVID-19, PPSV23, Shingrix, Tdap/Td, Hep A, Hep B, HPV, MMR, Varicella, Meningococcal — eligibility, dose counts, and intervals consistent with the current schedule. The COVID-19 and influenza entries deliberately defer to "the current CDC guidance" rather than hard-coding season-specific detail — appropriate. |

## Outcome

`DATA_VERIFIED` keys `red_flags`, `lasa_pairs`, `sig_abbreviations`,
`common_rx_flags`, and `vaccines` stay `False` until a pharmacist
signs the confirmation below. Once signed, set them to the sign-off
date; the SIG Decoder, Vaccine Eligibility, Drug Lookup, and Training
Center panels then stop showing the UNVERIFIED banner (Drug Lookup
and Training Center also depend on `brand_generic`, audited
separately). The `law` and `tpr` panels were out of scope this round.

**Pharmacist confirmation** (final clinical sign-off): ____________
Date: ____________
