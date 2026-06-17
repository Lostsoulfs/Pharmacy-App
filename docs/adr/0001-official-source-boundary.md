# 0001 - Official source boundary for training content

## Context

Pharmacy-App bundles training questions, reference lists, calculators, federal
law reminders, vaccine notes, TPR notes, and other pharmacy-technician study
content. The bundled data is useful for practice, but it is not professionally
validated and must not be presented as patient-care or professional-decision
content.

The upgrade campaign needs a durable rule for what sources may inform future
content review without implying that current bundled content is already
correct.

## Decision

`docs/OFFICIAL_SOURCES_2026.md` is the source boundary for future qualified
content review. It records official or primary starting points for PTCB exam
scope, federal controlled-substance requirements, vaccine schedules, FDA drug
safety communications, FDA clinical decision support guidance, HHS HIPAA
de-identification guidance, NIOSH hazardous-drug handling context, and GitHub
Actions security guidance.

Each app dataset domain is mapped separately in
`docs/DATA_SOURCE_REGISTER_2026.md`. Those mappings are review-routing
metadata only.

## Consequences

- A link to an official source does not validate any current question, answer,
  rule, medication record, vaccine entry, law entry, or TPR action.
- `DATA_VERIFIED` remains `False` for every dataset until a qualified
  pharmacist signs the corresponding audit artifact.
- State-specific pharmacy law is out of scope until a specific state track is
  approved and documented.

## Confirmation

Required confirmation for this foundation PR:

```bash
python tools/scan_staged.py --self-test
python tools/control_audit.py
python -m compileall -q pharmacy_app tests tools
pytest -q
```

Evidence level: IMPLEMENTED_UNVERIFIED until the draft PR checks pass.
