# 0003 - Training-only clinical and legal limit

## Context

Pharmacy-App contains clinical calculators, pharmacy-technician study prompts,
law notes, vaccine notes, drug lookup content, and TPR reminders. Those features
can look authoritative if the app does not repeat its boundary clearly.

## Decision

The app remains training software only:

- It must not be used for patient care, dispensing decisions, legal compliance
  decisions, or professional pharmacy decisions.
- Clinical and law datasets remain visibly UNVERIFIED until pharmacist signoff.
- Future FDA clinical decision support review is used to keep the app outside
  patient-care decision support framing, not to claim FDA clearance.
- Future HIPAA/HHS review is used to protect privacy boundaries, not to claim
  HIPAA de-identification.

## Consequences

- Content PRs must review one dataset domain at a time and cite current
  sources.
- No PR may flip `DATA_VERIFIED` without a signed, dated pharmacist review
  artifact under `docs/audits/`.
- UI or docs may improve how the warning is surfaced, but they must not soften
  the warning.

## Confirmation

Required confirmation for every content PR:

```bash
pytest tests/test_config.py tests/test_clinical_data.py tests/test_app_banners.py -q
```

Evidence level: POLICY_ADOPTED for this ADR; per-dataset data remains
UNVERIFIED.
