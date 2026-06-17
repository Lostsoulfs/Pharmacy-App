# 0008 - Scroll input hardening

## Context

Scrollable panels used one Windows-style mouse-wheel binding. The app needed
more predictable desktop scrolling without changing panel content or clinical
data.

## Decision

Centralize scroll bindings for scrollable panels:

- support Windows/macOS `<MouseWheel>` deltas,
- support Linux-style `<Button-4>` and `<Button-5>` wheel events,
- add keyboard scrolling for Up, Down, Page Up, Page Down, Home, and End,
- unbind every scroll sequence when views change,
- do not hijack key navigation while focus is in text-entry widgets.

## Consequences

- Long panels are easier to navigate on desktop.
- Scroll handlers are less likely to stack across panel re-renders.
- Display-free tests can verify event translation and input-widget guardrails.
- Touch/trackpad feel still needs manual desktop and Pydroid smoke testing.

## Confirmation

Required confirmation:

```bash
pytest tests/test_app_scroll_helpers.py -q
python -m compileall -q pharmacy_app tests tools
pytest -q
```

Evidence level: IMPLEMENTED_UNVERIFIED until local and CI checks pass.
