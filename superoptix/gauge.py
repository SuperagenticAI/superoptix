"""SuperGauge Agent Quality Record emission for SuperOptiX.

SuperQode emits records for coding-agent harnesses. This module does the same
for agents SuperOptiX compiles and serves, so one record format spans both a
repository harness and an agent running on any of the supported runtimes.

It adds one measure the coding-agent side has no equivalent for:
`interop.routing_invocation`, the rate at which a calling agent selects this
agent from a catalogue. For an agent reached over A2A, discoverability is a
quality dimension, and a skill nobody routes to has a completion rate nobody
observes.

Record format: https://github.com/SuperagenticAI/supergauge
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SUPERGAUGE_VERSION = "0.1"
MODEL_GRADED = frozenset({"answer.grounded", "robustness.multi_turn"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def scenario_manifest_digest(scenarios: list[dict[str, Any]], split: str = "held-out") -> str:
    """Fingerprint a BDD scenario split by name and expected output.

    SuperSpec scenarios are the task set for a compiled agent. Wording of the
    scenario text is excluded so an editorial change does not break a seal.
    """
    items = sorted(
        (
            str(s.get("name") or s.get("id") or ""),
            json.dumps(s.get("expected_output") or s.get("expect") or {}, sort_keys=True),
        )
        for s in scenarios
        if str(s.get("split") or "held-in") == split
    )
    return sha256_bytes(json.dumps(items, sort_keys=True).encode())


def _authority_from_playbook(playbook: dict[str, Any]) -> dict[str, Any]:
    """What the agent was permitted to do, read from the compiled playbook.

    Required by the specification: a record naming the agent without naming its
    permissions can be structurally valid and substantively wrong.
    """
    spec = playbook.get("spec") or playbook
    authority: dict[str, Any] = {}

    tools = spec.get("tools") or []
    names = sorted(
        str(t.get("name") if isinstance(t, dict) else t)
        for t in tools
        if (t.get("name") if isinstance(t, dict) else t)
    )
    if names:
        authority["capabilities"] = names

    runtime = spec.get("runtime") or {}
    sandbox = runtime.get("sandbox") or spec.get("sandbox")
    if sandbox:
        authority["sandbox"] = str(sandbox)

    network = runtime.get("network") or spec.get("network")
    if isinstance(network, dict):
        if network.get("allow") or network.get("allow_hosts"):
            authority["egress"] = "allow-list"
        elif network.get("enabled") is False:
            authority["egress"] = "deny-by-default"
        else:
            authority["egress"] = "unrestricted"

    return authority


def build_record(
    *,
    agent_name: str,
    playbook_path: str | Path,
    playbook: dict[str, Any],
    scenarios: list[dict[str, Any]],
    results: list[dict[str, Any]],
    framework: str,
    profile_id: str = "sg/framework-agent",
    profile_version: str = "0.1",
    tier: str = "T1",
    sealed: bool = False,
    canary_ids: list[str] | None = None,
    routing_metrics: Any = None,
    ledger: str | None = None,
    ledger_format: str = "opentelemetry/1.0",
    ledger_events: int | None = None,
    evaluator_independent: bool = False,
    actor: str | None = None,
) -> dict[str, Any]:
    """Project a `super agent evaluate` run into an Agent Quality Record.

    Measures appear only where the run produced them. An evaluation without
    repeated attempts carries no reliability measure and reaches L2 at best,
    which is the accurate outcome rather than a flattering one.
    """
    held_in = sum(1 for s in scenarios if str(s.get("split") or "held-in") == "held-in")
    held_out = sum(1 for s in scenarios if str(s.get("split") or "held-in") == "held-out")

    measures: list[dict[str, Any]] = []
    gates: list[dict[str, Any]] = []

    scored = [r for r in results if r.get("status") in {"passed", "failed"}]
    if scored:
        passed = sum(1 for r in scored if r.get("status") == "passed")
        measures.append(
            {
                "id": "task.completion",
                "value": round(passed / len(scored), 3),
                "n": len(scored),
            }
        )

    # Discoverability. Only meaningful for an agent published over A2A, so it is
    # omitted rather than defaulted when no routing evaluation ran.
    if routing_metrics is not None:
        rate = getattr(routing_metrics, "invocation_rate", None)
        if rate is None and isinstance(routing_metrics, dict):
            rate = routing_metrics.get("invocationRate") or routing_metrics.get("invocation_rate")
        if rate is not None:
            measures.append({"id": "interop.routing_invocation", "value": round(float(rate), 3)})

    usage = _aggregate_usage(results)
    successes = sum(1 for r in results if r.get("status") == "passed")
    if successes and usage.get("total_tokens"):
        measures.append(
            {
                "id": "efficiency.tokens_per_success",
                "value": round(usage["total_tokens"] / successes, 1),
            }
        )
    if successes and usage.get("cost_usd"):
        measures.append(
            {
                "id": "efficiency.cost_per_success",
                "value": round(usage["cost_usd"] / successes, 6),
                "unit": "usd",
            }
        )

    evidence: dict[str, Any] = {"format": ledger_format, "replayable": bool(ledger)}
    if ledger:
        evidence["ledger"] = str(ledger)
    if ledger_events is not None:
        evidence["events"] = int(ledger_events)

    task_set: dict[str, Any] = {
        "manifest_digest": scenario_manifest_digest(scenarios, "held-out"),
        "held_in": held_in,
        "held_out": held_out,
        "sealed": bool(sealed),
    }
    if canary_ids:
        task_set["canary_ids"] = list(canary_ids)

    subject: dict[str, Any] = {
        "agent": agent_name,
        "harness_digest": sha256_file(playbook_path),
        "authority": _authority_from_playbook(playbook),
    }
    model = (playbook.get("spec") or {}).get("language_model") or {}
    if model.get("provider") and model.get("model"):
        subject["model"] = {"provider": str(model["provider"]), "id": str(model["model"])}

    return {
        "supergauge": SUPERGAUGE_VERSION,
        "record_id": f"aqr_{secrets.token_hex(8)}",
        "emitted_at": _now(),
        "profile": {"id": profile_id, "version": profile_version, "tier": tier},
        "subject": subject,
        "task_set": task_set,
        "measures": measures,
        "gates": gates,
        "assurance": {
            "evidence": evidence,
            "evaluator_independent": bool(evaluator_independent),
        },
        "decision": {
            "verdict": "hold",
            "actor": actor or os.environ.get("USER") or "unknown",
        },
        # Advisory. Names the runtime the record was produced against, so a
        # reader comparing two records knows whether they are comparable.
        "x-superoptix": {"framework": framework},
    }


def _aggregate_usage(results: list[dict[str, Any]]) -> dict[str, float]:
    total_tokens = 0.0
    cost = 0.0
    for result in results:
        usage = result.get("usage") or {}
        total_tokens += float(usage.get("total_tokens") or 0)
        cost += float(usage.get("cost_usd") or 0)
    return {"total_tokens": total_tokens, "cost_usd": cost}


def add_reliability(record: dict[str, Any], runs: list[list[dict[str, Any]]]) -> None:
    """Add pass^k and pass@k across independent evaluation runs.

    Attempts must be independent: no shared memory, and agent state reset
    between them. Where that cannot be guaranteed the measure is unsound and
    should be omitted.
    """
    per_task: dict[str, list[bool]] = {}
    for run in runs:
        for result in run:
            if result.get("status") in {"passed", "failed"}:
                key = str(result.get("id") or result.get("name") or "")
                per_task.setdefault(key, []).append(result["status"] == "passed")

    k = len(runs)
    complete = {t: r for t, r in per_task.items() if len(r) == k}
    if not complete or k < 2:
        return

    n = len(complete)
    record["measures"].append(
        {
            "id": "reliability.pass_hat_k",
            "value": round(sum(1 for r in complete.values() if all(r)) / n, 3),
            "k": k,
            "n": n,
        }
    )
    record["measures"].append(
        {
            "id": "reliability.pass_at_k",
            "value": round(sum(1 for r in complete.values() if any(r)) / n, 3),
            "k": k,
            "n": n,
        }
    )
