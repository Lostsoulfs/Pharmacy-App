# CLAUDE.md

> **Read this even if you are not Claude.** This file is auto-loaded by Claude Code, but
> the rules here are not Claude-specific. The canonical, tool-agnostic contract for every
> AI agent (and human) in this repo is **[`AGENTS.md`](AGENTS.md)** — read it first,
> whoever you are. Below are only Claude-Code-specific notes.

Pharmacy-technician PTCB-prep training app (Pydroid 3 / Tkinter / SQLite, offline,
single user). **The architecture map, clinical-data rules (ADR-C05 / `DATA_VERIFIED`),
conventions, testing layers, and boundaries all live in [`AGENTS.md`](AGENTS.md)** —
they were moved there so no agent can miss them by skipping a Claude-named file.
Read `SECURITY.md` before writes, deletes, installs, credential work, or outbound
actions.

## Claude-specific notes

- For subagents, tell them to read `AGENTS.md` and `SECURITY.md` first, then report
  verified versus assumed facts.
- Do not edit `.claude/`, hooks, settings, or agent permissions unless explicitly asked.
- If push or a tool call is blocked, report the exact blocker and the next safe option.
  Do not claim persistence until the remote branch or commit is verified.
