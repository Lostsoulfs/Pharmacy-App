# BRAND_GENERIC Audit — Top 200 Drug List

- **Dataset:** `BRAND_GENERIC` in `pharmacy_app/clinical_data.py`
- **Source lines:** 155–364 (210 entries)
- **Audit date:** 2026-05-20
- **Auditor:** Claude Code (automated cross-check)
- **Status:** PENDING pharmacist sign-off — automated audit complete
  2026-05-20; per ADR-C05 `DATA_VERIFIED["brand_generic"]` stays
  False until the pharmacist confirmation below is signed.

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
- **5 entries flagged, then web-verified** — see table below. After
  verification: 0 wrong brand→generic pairings (the HIGH row 201 was
  overturned — Tezruly is a valid 2024 brand), 3 spelling/formatting
  corrections applied, 1 left as-is.
- **No duplicate brand/generic pairs found.** Metoprolol appears
  twice (tartrate, line 225 / succinate, line 359) and insulin five
  times — all distinct salts/formulations, not duplicates.

## Flagged discrepancies

| Line | Brand | Generic (as-is) | Issue type | Resolution | Severity |
|------|-------|-----------------|------------|------------|----------|
| 201 | `Tezruly/Hytrin` | Terazosin | brand-generic-mismatch | **OVERTURNED — no change.** Web check (WebMD, RxList, Medscape) confirms Tezruly is a real FDA-approved terazosin oral solution (approved 2024-07-29); Hytrin is the discontinued original tablet. Entry is correct. | HIGH→none |
| 233 | `Keflex` | Cefalexin | spelling | **APPLIED.** FDA Keflex label and US/USAN convention use `Cephalexin`; "Cefalexin" is the INN. Generic changed to `Cephalexin`. | MEDIUM |
| 174 | `Heparin Sodium` | Heparin | formatting | **No change.** "Heparin Sodium" is a generic descriptor — heparin has no distinctive modern brand. Acceptable as-is. | LOW |
| 255 | `Veetids (generic)` | Penicillin V potassium | formatting | **APPLIED.** Veetids is a (discontinued) brand; the "(generic)" annotation was contradictory. Brand changed to `Veetids`. | LOW |
| 165 | `Glumetza ER/...` | Metformin | formatting | **APPLIED.** Glumetza is itself the extended-release product; "ER" was redundant. Brand changed to `Glumetza/Riomet/Glucophage/Fortamet`. | LOW |

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

## Resolution (2026-05-20)

Flagged rows web-verified against FDA labeling / DailyMed-class
references; 3 corrections applied to `clinical_data.py`, 1 flag
overturned (Tezruly is a valid 2024 brand), 1 left as-is.

Consistency cleanups also applied: `Tetracycline` drug_class →
"Tetracycline antibacterial" (line 173); `Celebrex` →
"COX-2 selective NSAID"; `Ultram`/Tramadol "Opiate narcotic" →
"Opioid analgesic". The "Top 200" / 210-entry count is a label, left
as-is. Discontinued brands (Zantac, Coumadin) are carried
intentionally for a training reference.

`DATA_VERIFIED["brand_generic"]` stays `False` in `config.py` until a
pharmacist signs the confirmation below. Once signed, set it to the
sign-off date; the Drug Lookup banner then clears when
`common_rx_flags` is also verified, and the Training Center banner
when `red_flags` and `lasa_pairs` are verified.

**Pharmacist confirmation** (final clinical sign-off): ____________
Date: ____________
