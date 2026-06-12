# CLAUDE.md

The filename is historical. This is a universal instruction source for every human,
agent, and automation system working in this repository. Read it together with
`AGENTS.md` and `SECURITY.md`; all rules below apply regardless of the tool in use.

Pharmacy-technician PTCB-prep training app (Pydroid 3 / Tkinter / SQLite, offline,
single user). **The architecture map, clinical-data rules (ADR-C05 / `DATA_VERIFIED`),
conventions, testing layers, and boundaries all live in [`AGENTS.md`](AGENTS.md)** —
they were moved there so no agent can miss them by skipping a Claude-named file.
Read `SECURITY.md` before writes, deletes, installs, credential work, or outbound
actions.

## Operational notes

- For subagents, tell them to read `AGENTS.md` and `SECURITY.md` first, then report
  verified versus assumed facts.
- Do not edit `.claude/`, hooks, settings, or agent permissions unless explicitly asked.
- If push or a tool call is blocked, report the exact blocker and the next safe option.
  Do not claim persistence until the remote branch or commit is verified.
