# Law & TPR Panel Audit — LAW_BULLETS, TPR_CODES

- **Datasets:** `LAW_BULLETS` and `TPR_CODES` in `clinical_data.py`
  (new — back the `panel_law` and `panel_tpr` UI panels).
- **Audit date:** 2026-05-20
- **Auditor:** Claude Code, from pharmacist-commissioned deep-research
  documents.
- **Status:** PENDING pharmacist sign-off — built from
  pharmacist-commissioned research; per ADR-C05 `DATA_VERIFIED` keys
  `law` and `tpr` stay False until the pharmacist confirmation below
  is signed.

## Background

Before this audit the `law` and `tpr` panels rendered short hardcoded
lists carried from the v13 source and were the last two `UNVERIFIED`
domains. Two deep-research documents were commissioned and delivered
to Drive:

- *Mississippi Pharmacy Law and Dispensing Regulations (2026)* —
  cited to Miss. Admin. Code Title 30 Part 3001, MS Code Ann.
  Title 73 ch. 21 and Title 41 ch. 29, and MS Board of Pharmacy
  publications.
- *Pharmacy Third-Party Claim Rejection Mitigation and Adjudication
  Workflows (2026)* — cited to NCPDP Telecommunication Standard D.0
  reject codes and PBM payer sheets (CVS Caremark, Prime Therapeutics,
  Medi-Cal Rx, Alabama/Colorado/Michigan Medicaid).

Both documents were reviewed for quality and judged authoritative and
well-sourced.

## LAW_BULLETS — 25 entries, 6 categories

Extracted from the Mississippi law document: technician registration
and scope, controlled substances, the Prescription Monitoring
Program, valid prescriptions, emergency dispensing and counseling,
and records and inventory. Content reflects the cited MS Board
regulations.

**Forward-looking item flagged:** the technician-to-pharmacist
staffing-ratio bullet states the current 3:1 rule and notes the
pending HB1675 increase (5:1 community / 12:1 closed-door, effective
July 1 2026). HB1675 was cited "as introduced" — a bill, not yet
codified at the audit date. The bullet presents 3:1 as the rule in
force and clearly labels the HB1675 change as pending; re-verify
after July 1 2026.

## TPR_CODES — 15 entries

The most common NCPDP claim reject codes a pharmacy technician
encounters, each with its meaning and the concrete resolution step.
Code 88 (DUR reject) is explicitly marked as requiring the
pharmacist, consistent with the scope-of-practice division in the
source document. Closely related codes are paired where a technician
treats them identically (21/54 invalid NDC, 25/56 prescriber ID,
70/MR non-formulary).

## Outcome

`panel_law` and `panel_tpr` now render these datasets instead of the
hardcoded v13 lists. `DATA_VERIFIED["law"]` and `["tpr"]` stay
`False` until a pharmacist signs the confirmation below; until then
both panels show the UNVERIFIED banner. All 8 verification domains
remain unverified pending pharmacist sign-off.

State law and payer rules change. Re-verify `LAW_BULLETS` against the
current MS Board regulations periodically (and after HB1675 takes
effect), and `TPR_CODES` against current NCPDP/PBM documentation.

**Pharmacist confirmation** (final sign-off): ____________
Date: ____________
