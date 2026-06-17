#!/usr/bin/env python3
"""Validate repository engineering controls against .github/control-policy.json."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("control-audit: PyYAML is required (pip install PyYAML==6.0.3)", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / ".github" / "control-policy.json"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
ACTION = re.compile(
    r"^(?P<owner>[^/]+)/(?P<repo>[^/@]+)(?:/[^@]+)?@(?P<ref>.+)$"
)
PIP_INSTALL = re.compile(r"\b(?:python\s+-m\s+)?pip\s+install\b")


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream) or {}
    if not isinstance(data, dict):
        raise ValueError("top level must be a mapping")
    return data


def events(data: dict) -> object:
    return data.get("on", data.get(True, {}))


def has_event(data: dict, event: str) -> bool:
    configured = events(data)
    if isinstance(configured, str):
        return configured == event
    if isinstance(configured, list):
        return event in configured
    if isinstance(configured, dict):
        return event in configured
    return False


def permission_writes(value: object) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        return {"*"} if value == "write-all" else set()
    if not isinstance(value, dict):
        return {"<invalid>"}
    return {str(name) for name, level in value.items() if level == "write"}


def read_only_permissions(value: object) -> bool:
    if value == "read-all":
        return True
    if not isinstance(value, dict):
        return False
    for level in value.values():
        if level not in {"read", "none"}:
            return False
    return True


def run_installs_tool(run: str, tool: str) -> bool:
    if not PIP_INSTALL.search(run):
        return False
    pattern = rf"(?<![\w.-]){re.escape(tool)}(?=[\s'\"<>=]|$)"
    return re.search(pattern, run) is not None


def main() -> int:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    exceptions = {
        (item["code"], item.get("path", "*")): item["reason"]
        for item in policy.get("exceptions", [])
    }
    failures: list[str] = []
    waived: list[str] = []
    tool_pins = policy.get("workflow_tool_pins", {})
    allowed_writes = {
        (item["workflow"], item["job"], item["permission"])
        for item in policy.get("allowed_job_write_permissions", [])
    }

    def report(code: str, path: str, message: str) -> None:
        reason = exceptions.get((code, path)) or exceptions.get((code, "*"))
        line = f"{code} {path}: {message}"
        if reason:
            waived.append(f"{line} [waived: {reason}]")
        else:
            failures.append(line)

    for required in policy["required_files"]:
        path = ROOT / required
        if not path.is_file() or path.stat().st_size == 0:
            report("required-file", required, "missing or empty")

    for instruction in policy["instruction_sources"]:
        path = ROOT / instruction
        if not path.is_file() or len(path.read_text(encoding="utf-8").strip()) < 40:
            report("instruction-source", instruction, "must remain a substantive universal instruction source")

    for nested in policy.get("nested_instruction_files", []):
        if not (ROOT / nested).is_file():
            report("nested-instructions", nested, "declared nested instruction file is missing")

    workflows = sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix in {".yml", ".yaml"}
        and not {".git", "node_modules", ".nox", ".venv", "venv"}.intersection(path.parts)
        and path.parent.name == "workflows"
        and path.parent.parent.name == ".github"
    )
    names: set[str] = set()
    for workflow in workflows:
        rel = workflow.relative_to(ROOT).as_posix()
        text = workflow.read_text(encoding="utf-8")
        try:
            data = load_yaml(workflow)
        except Exception as exc:
            report("workflow-yaml", rel, str(exc))
            continue

        name = data.get("name")
        if isinstance(name, str):
            names.add(name)
        else:
            report("workflow-name", rel, "workflow requires a stable name")

        if "permissions" not in data:
            report("workflow-permissions", rel, "top-level permissions are required")
        elif not read_only_permissions(data["permissions"]):
            report(
                "workflow-permissions",
                rel,
                "top-level permissions must be read-only",
            )
        concurrency = data.get("concurrency")
        if not isinstance(concurrency, dict):
            report("workflow-concurrency", rel, "concurrency must define group and cancellation")
        else:
            group = concurrency.get("group")
            if not isinstance(group, str) or "github.ref" not in group:
                report("workflow-concurrency", rel, "concurrency.group must be scoped by github.ref")
            cancel = concurrency.get("cancel-in-progress")
            conditional_cancel = isinstance(cancel, str) and cancel.strip().startswith("${{")
            if cancel is not True and not conditional_cancel:
                report("workflow-concurrency", rel, "concurrency.cancel-in-progress must be true or conditional")
        if has_event(data, "pull_request_target"):
            report("pull-request-target", rel, "pull_request_target is prohibited")

        if "ref: ${{ github.head_ref }}" in text:
            report("fork-checkout", rel, "pull request jobs must use the read-only event checkout")

        jobs = data.get("jobs", {})
        if not isinstance(jobs, dict) or not jobs:
            report("workflow-jobs", rel, "workflow must define jobs")
            continue

        if name == "secret-pii-scan":
            trusted_checkout = False
            for job in jobs.values():
                if not isinstance(job, dict):
                    continue
                for step in job.get("steps", []) or []:
                    if not isinstance(step, dict):
                        continue
                    with_values = step.get("with", {}) or {}
                    uses = step.get("uses")
                    if (
                        isinstance(uses, str)
                        and uses.startswith("actions/checkout@")
                        and with_values.get("path") == "scanner_dir"
                        and with_values.get("ref") == "${{ github.base_ref }}"
                        and with_values.get("persist-credentials") is False
                    ):
                        trusted_checkout = True
            if not trusted_checkout:
                report(
                    "trusted-scanner",
                    rel,
                    "secret scan must check out scanner from base branch",
                )
            if "scanner_dir/tools/scan_staged.py --self-test" not in text:
                report("trusted-scanner", rel, "trusted scanner self-test is required")
            if "scanner_dir/tools/scan_staged.py --ci" not in text:
                report("trusted-scanner", rel, "trusted scanner must scan the PR diff")

        for job_id, job in jobs.items():
            if not isinstance(job, dict):
                report("workflow-job", rel, f"job {job_id} must be a mapping")
                continue
            for permission in permission_writes(job.get("permissions")):
                if (str(name), str(job_id), permission) not in allowed_writes:
                    report(
                        "job-permission-write",
                        rel,
                        f"job {job_id} has undeclared write permission {permission}",
                    )
            if "timeout-minutes" not in job:
                report("job-timeout", rel, f"job {job_id} requires timeout-minutes")
            if "head.repo.full_name == github.repository" in str(job.get("if", "")):
                report("fork-scan", rel, f"job {job_id} must not skip fork pull requests")
            for step in job.get("steps", []) or []:
                if not isinstance(step, dict):
                    continue
                uses = step.get("uses")
                run = step.get("run")
                if isinstance(run, str):
                    for tool, version in tool_pins.items():
                        if (
                            run_installs_tool(run, tool)
                            and f"{tool}=={version}" not in run
                        ):
                            report(
                                "workflow-tool-pin",
                                rel,
                                f"{tool} installs must pin {tool}=={version}",
                            )
                if isinstance(uses, str):
                    match = ACTION.match(uses)
                    if match and not FULL_SHA.fullmatch(match.group("ref")):
                        report(
                            "action-pin",
                            rel,
                            f"{uses} is not pinned to a full commit SHA",
                        )
                    if uses.startswith("actions/checkout@"):
                        with_values = step.get("with", {}) or {}
                        if with_values.get("persist-credentials") is not False:
                            report(
                                "checkout-credentials",
                                rel,
                                "actions/checkout must set persist-credentials: false",
                            )

    for required_workflow in policy["required_workflows"]:
        if required_workflow not in names:
            report("required-workflow", required_workflow, "stable workflow name not found")

    for item in waived:
        print(f"WAIVED {item}")
    if failures:
        for item in failures:
            print(f"ERROR {item}", file=sys.stderr)
        print(f"control-audit: {len(failures)} failure(s), {len(waived)} documented waiver(s)", file=sys.stderr)
        return 1

    print(
        f"control-audit: PASS ({len(workflows)} workflows, "
        f"{len(waived)} documented waiver(s), scanner={policy['scanner_mode']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
