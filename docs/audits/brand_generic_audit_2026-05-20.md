# BRAND_GENERIC Audit — Top 200 Drug List

- **Dataset:** `BRAND_GENERIC` in `pharmacy_app/clinical_data.py`
- **Source lines:** 155–364 (210 entries)
- **Audit date:** 2026-05-20
- **Auditor:** Claude Code (automated cross-check)
- **Status:** AWAITING PHARMACIST SIGN-OFF

## Methodology

Each of the 210 entries was cross-checked for: brand→generic
correctness, `drug_class` accuracy, spelling against US/USAN
convention, discontinued/withdrawn brands, duplicate entries, and
field formatting. This is an automated screen against well-established
brand↔generic knowledge — it is **not** an authoritative reference.
The pharmacist must confirm every flagged row (and is encouraged to
spot-check unflagged rows) against an authoritative source — PTCB
reference list, Lexicomp, or the current FDA Orange Book — before
sign-off.

## Summary

- 210 entries reviewed.
- **205 entries: no finding** — brand, generic, and drug_class
  consistent with established references.
- **5 entries flagged** — see table below. None are outright wrong
  brand→generic pairings except the high-severity row 201; the
  remainder are spelling/formatting/consistency items.
- **No duplicate brand/generic pairs found.** Metoprolol appears
  twice (tartrate, line 225 / succinate, line 359) and insulin five
  times — all distinct salts/formulations, not duplicates.

## Flagged discrepancies

| Line | Brand | Generic (as-is) | Issue type | Finding / proposed correction | Severity |
|------|-------|-----------------|------------|-------------------------------|----------|
| 201 | `Tezruly/Hytrin` | Terazosin | brand-generic-mismatch | "Tezruly" is not a recognized terazosin brand and appears to be a garbled entry from the salvaged crunch bundle. Hytrin is the established brand. **Proposed:** drop "Tezruly", set brand to `Hytrin`. | HIGH |
| 233 | `Keflex` | Cefalexin | spelling | "Cefalexin" is the INN spelling; US/USAN convention (and how it appears on US labels) is **Cephalexin**. **Proposed:** change generic to `Cephalexin`. | MEDIUM |
| 174 | `Heparin Sodium` | Heparin | formatting | The `brand` field holds a generic descriptor, not a trade name — heparin has no distinctive modern brand. **Proposed:** acceptable to leave, or note that no brand applies. | LOW |
| 255 | `Veetids (generic)` | Penicillin V potassium | formatting | "Veetids" *is* the brand; the "(generic)" annotation is contradictory. **Proposed:** change brand to `Veetids`. | LOW |
| 165 | `Glumetza ER/...` | Metformin | formatting | "Glumetza ER" is redundant — Glumetza is itself the extended-release product. **Proposed:** `Glumetza` (the ER is implicit) or `Glucophage XR`. | LOW |

## Consistency notes (not errors — pharmacist's discretion)

These are internal-consistency observations, not factual errors. Fix
only if desired for display polish:

- **`drug_class` wording drift.** Tetracycline is "Antibacterial"
  (line 173) but "Tetracycline antibacterial" (line 348). Tramadol is
  "Opiate narcotic" (line 341) while other opioids use "Opioid"
  (e.g. lines 156, 251). Amoxicillin is "Antibacterial" (line 160)
  vs the more specific classes used elsewhere.
- **Line 207, Celebrex** — `drug_class` "COX-inhibitor/NSAID"; the
  slash can read as a combination drug. "COX-2 selective NSAID" is
  clearer.
- **Line 220, Depacon/Depakote** — generic listed as "Valproate
  sodium"; Depakote is divalproex sodium (a different salt). Consider
  "Divalproex / valproate sodium".
- **Line 226, Robitussin** — generic "Dextromethorphan/Guaifenesin"
  describes Robitussin **DM**; plain Robitussin is guaifenesin only.
- **Discontinued brands carried intentionally** — Zantac/Ranitidine
  (line 360, already annotated "withdrawn 2020") and Coumadin
  (line 345, brand discontinued). Fine for a training reference;
  noted for awareness.
- **Entry count.** The header comment says "Top 200" but the list has
  210 entries. Either trim to 200 or update the comment.

## Sign-off

- [ ] Pharmacist reviewed all 5 flagged rows and the consistency notes.
- Reviewed by: ______________________  Date: ____________
- Decision (circle): APPROVE AS-IS / APPROVE WITH CORRECTIONS / REJECT

**On sign-off:** apply the agreed corrections to
`pharmacy_app/clinical_data.py` (lines 155–364), then set
`DATA_VERIFIED["brand_generic"] = True` in `pharmacy_app/config.py`.
That will clear the UNVERIFIED banner on the Drug Lookup panel; the
Training Center banner will also clear once `red_flags` and
`lasa_pairs` are verified.
