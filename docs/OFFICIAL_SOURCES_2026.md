# Official Source Boundary

Reviewed June 17, 2026.

This application is training software only. It is not a clinical decision
system, dispensing system, legal compliance system, or professional pharmacy
reference. The bundled data has not been professionally validated.

The sources below are authoritative starting points for future qualified review.
Adding a source link does not validate the application's current questions,
answers, calculations, rules, medication data, vaccine notes, law notes, or TPR
content.

## Source Register

| ID | Source | Authority level | Covered domains | Review use |
| --- | --- | --- | --- | --- |
| SRC-PTCB-2026-PTCE | [PTCB PTCE Content Outline effective January 6, 2026](https://ptcb.org/wp-content/uploads/2025/07/PTCE-Content-Outline.pdf) | Official certification-exam source | PTCB readiness, study coverage, domain mapping | Map training topics to exam domains; do not treat as item-level validation. |
| SRC-PTCB-2026-KNOWLEDGE | [PTCB 2026 CPhT Knowledge Reference](https://ptcb.org/wp-content/uploads/2025/05/cpht-knowledge-reference.pdf) | Official certification knowledge reference | PTCB topic details | Support future gap review against required/recommended knowledge areas. |
| SRC-DEA-PHARMACIST-MANUAL | [DEA Pharmacist's Manual](https://www.deadiversion.usdoj.gov/GDP/%28DEA-DC-046R1%29%28EO-DEA154R1%29_Pharmacist%27s_Manual_DEA.pdf) | Federal agency guidance | Controlled-substance federal law, DEA schedules, prescription handling | Review federal controlled-substance training prompts and DEA-related tool text. |
| SRC-DEA-CSA | [DEA Controlled Substances Act overview](https://www.dea.gov/drug-information/csa) | Federal agency overview | Controlled-substance background | Use only as an overview; prefer the manual/regulations for specific review. |
| SRC-CDC-VACCINE-SCHEDULES | [CDC immunization schedules for healthcare providers](https://www.cdc.gov/vaccines/hcp/imz-schedules/index.html) | Federal public-health schedule source | Vaccine eligibility/training notes | Review vaccine schedule content against current provider schedules. |
| SRC-FDA-DRUG-SAFETY | [FDA Drug Safety Communications](https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications) | Federal drug-safety communication source | Red flags, severe adverse effects, medication safety notes | Check whether training warnings align with current FDA safety communications. |
| SRC-FDA-CDS-GUIDANCE | [FDA Clinical Decision Support Software guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software) | Federal regulatory guidance | App boundary, training-only wording, calculator/reference framing | Keep the app out of patient-care decision-support claims. |
| SRC-HHS-HIPAA-DEID | [HHS HIPAA de-identification guidance](https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html) | Federal privacy guidance | Privacy boundary, PHI handling, data tiers | Inform privacy guardrails; does not certify this repo as de-identified. |
| SRC-NIOSH-HAZARDOUS-DRUGS | [NIOSH List of Hazardous Drugs in Healthcare Settings, 2024](https://www.cdc.gov/niosh/docs/2025-103/default.html) | Federal occupational-health source | Hazardous-drug handling, safety training context | Review hazardous-drug handling references where in scope. |
| SRC-TN-BOP | [Tennessee Board of Pharmacy](https://www.tn.gov/health/licensure/pharm.html) | State board source | Possible future Tennessee-specific track | Do not generalize to other states; use only after approving a Tennessee track. |
| SRC-GITHUB-ACTIONS-SECURE-USE | [GitHub Actions secure use reference](https://docs.github.com/en/actions/reference/security/secure-use) | Platform security documentation | Workflow hardening, token permissions, third-party action handling | Inform CI/security governance, not app pharmacy content. |

## Review Rules

- Keep every dataset `UNVERIFIED` until a qualified pharmacist signs the
  matching review artifact under `docs/audits/`.
- Review one dataset domain per content PR. Do not mix unrelated clinical/law
  rewrites into governance or tooling PRs.
- Cite the source ID and review date for every changed item.
- If the source is federal/PTCB, do not present it as state-specific pharmacy
  law.
- If state-specific law is needed, create a separate state track and cite the
  state board or official state rules.
- Rerun tests after every content correction.

## Related Records

- `docs/DATA_SOURCE_REGISTER_2026.md` maps current app dataset keys to source
  candidates and review status.
- `docs/adr/0001-official-source-boundary.md` records this source-boundary
  decision.
- `docs/adr/0003-training-only-clinical-legal-limit.md` records the
  training-only clinical/legal boundary.
