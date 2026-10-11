"""SuperGauge Agent Quality Record emission for SuperOptiX.

SuperQode emits records for coding-agent harnesses. This module does the same
for agents SuperOptiX compiles and serves, so one record format spans both a
repository harness and an agent running on any of the supported runtimes.

It adds one measure the coding-agent side has no equivalent for:
`interop.routing_invocation`, the rate at which a calling agent selects this
agent from a catalogue. For an agent reached over A2A, discoverability is a
quality dimension: where selection fails, the agent receives no work, and its
completion rate describes traffic that never arrived.

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


def scenario_manifest_digest(
    scenarios: list[dict[str, Any]], split: str = "held-out"
) -> str:
    """Fingerprint a BDD scenario split by name and expected output.

    SuperSpec scenarios are the task set for a compiled agent. Wording of the
    scenario text is excluded so an editorial change does not break a seal.
    """
    items = sorted(
        (
            str(s.get("name") or s.get("id") or ""),
            json.dumps(
                s.get("expected_output") or s.get("expect") or {}, sort_keys=True
            ),
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
        authority["capabilities"] = sorted(set(names))

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

    # SuperGauge requires grant_digest or acs_policy_version. SuperOptiX has no
    # ACS policy, so the grant is the authority-relevant playbook content in
    # force for the run (tools, runtime, sandbox, network), digested.
    grant = {
        "tools": spec.get("tools") or [],
        "runtime": spec.get("runtime") or {},
        "sandbox": spec.get("sandbox"),
        "network": spec.get("network"),
    }
    authority["grant_digest"] = sha256_bytes(
        json.dumps(grant, sort_keys=True, default=str).encode()
    )
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
    which is the accurate outcome.
    """
    held_in = sum(1 for s in scenarios if str(s.get("split") or "held-in") == "held-in")
    held_out = sum(
        1 for s in scenarios if str(s.get("split") or "held-in") == "held-out"
    )

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
    # omitted, never defaulted, when no routing evaluation ran.
    if routing_metrics is not None:
        rate = getattr(routing_metrics, "invocation_rate", None)
        if rate is None and isinstance(routing_metrics, dict):
            rate = routing_metrics.get("invocationRate") or routing_metrics.get(
                "invocation_rate"
            )
        if rate is not None:
            measures.append(
                {"id": "interop.routing_invocation", "value": round(float(rate), 3)}
            )

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
        subject["model"] = {
            "provider": str(model["provider"]),
            "id": str(model["model"]),
        }

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


def apply_jev_judgment(
    record: dict[str, Any],
    judgment: Any,
    *,
    min_confidence: float = 0.75,
    threshold_version: dict[str, Any] | None = None,
    judged_measure_id: str | None = None,
) -> dict[str, Any]:
    """Project a System One Disposition onto an existing Agent Quality Record.

    Records Choice advice. Acceptance preserves an existing approval; warn holds.
    Soft-holds accept when confidence is below ``min_confidence``. Pins
    ``assurance.judge`` when model / pack_digest are present. Never inserts a
    gate on confidence, Score, or Noul (SPEC §4.1 / RFC 0004).

    ``judged_measure_id`` defaults to omitting a new measure. Pass an existing
    registry id such as ``answer.grounded`` only when the Score grades that
    property; do not invent ids here.
    """
    from superoptix.quality.jev import (
        DEFAULT_MODEL_HINT,
        judgment_from_choice_object,
        pin_assurance_judge,
        resolve_verdict,
    )

    disposition = judgment_from_choice_object(judgment)
    verdict, soft_rationale = resolve_verdict(
        disposition.choice,
        disposition.confidence,
        min_confidence=min_confidence,
    )

    decision = dict(record.get("decision") or {})
    previous_verdict = decision.get("verdict")
    gates = record.get("gates") or []
    preservation_note = None
    if previous_verdict == "reject":
        verdict = "reject"
        preservation_note = "Existing rejection retained."
    elif verdict == "ship":
        # Acceptance is advice. It can only retain approval already recorded.
        if (
            disposition.source.startswith("heuristic")
            or previous_verdict != "ship"
            or not gates
            or any(
                gate.get("result") != "pass" or gate.get("id") in MODEL_GRADED
                for gate in gates
            )
            or not (record.get("task_set") or {}).get("sealed")
        ):
            verdict = "hold"
            preservation_note = "Judge acceptance requires separate release approval and passing deterministic checks."
    from superoptix.gauge_checks import mechanical_override

    if mechanical_override(record, disposition.choice == "accept"):
        verdict = "reject" if verdict == "reject" else "hold"
        preservation_note = (
            (preservation_note + " ") if preservation_note else ""
        ) + "Deterministic integrity failed; judged acceptance overridden (RFC 0005)."
    decision["verdict"] = verdict
    parts = [
        p
        for p in (
            decision.get("rationale"),
            disposition.rationale,
            soft_rationale,
            preservation_note,
            (
                f"Choice {disposition.choice!r} (confidence "
                f"{disposition.confidence:.2f}) → AQR {verdict}."
            ),
        )
        if p
    ]
    decision["rationale"] = " ".join(parts)
    record["decision"] = decision

    if not disposition.source.startswith("heuristic"):
        model = disposition.model or DEFAULT_MODEL_HINT
        record["assurance"] = pin_assurance_judge(
            record.get("assurance"),
            model=model,
            pack_digest=disposition.pack_digest,
            judge_id=disposition.judge_id,
        )

    measures = list(record.get("measures") or [])
    if judged_measure_id and disposition.score is not None:
        # Only when caller names an existing judged registry id.
        if judged_measure_id in MODEL_GRADED or judged_measure_id.startswith("answer."):
            measures.append(
                {
                    "id": judged_measure_id,
                    "value": round(float(disposition.score), 3),
                    "n": 1,
                }
            )
            record["measures"] = measures

    meta = dict(record.get("x-superoptix") or {})
    jev_meta: dict[str, Any] = {
        "disposition": disposition.to_dict(),
        "min_confidence": float(min_confidence),
        "source": disposition.source,
        "confidence_kind": "proxy"
        if disposition.source.startswith("heuristic")
        else "judge-reported",
        "choice_to_verdict": {
            "accept": "retain existing approval",
            "warn": "hold",
            "reject": "reject",
        },
        "release_authorization": "acceptance cannot authorize ship",
        "l1_note": (
            "Jev is advisory: it can soft-hold or reject, never ship, and never "
            "backs a gate. L2 comes from deterministic gates, a sealed held-out "
            "split and canary probes (super agent test)."
        ),
    }
    if disposition.requested_model and disposition.requested_model != (
        disposition.model
    ):
        jev_meta["requested_model"] = disposition.requested_model
    if not disposition.source.startswith("heuristic"):
        jev_meta["model_source"] = "served" if disposition.model_served else "requested"
    if threshold_version:
        jev_meta["threshold_version"] = threshold_version
    meta["jev"] = jev_meta
    record["x-superoptix"] = meta
    return record


def sidecar_path(out_path: str | Path) -> Path:
    """Where SuperOptiX metadata for a record is written (``<stem>.superoptix.json``)."""
    destination = Path(out_path)
    return destination.with_name(destination.stem + ".superoptix.json")


def ledger_path_for(out_path: str | Path) -> Path:
    """Evaluation ledger written next to a record (``<stem>.ledger.jsonl``)."""
    destination = Path(out_path)
    return destination.with_name(destination.stem + ".ledger.jsonl")


def write_ledger(path: str | Path, runs: list[list[dict[str, Any]]]) -> int:
    """Write per-run, per-scenario evaluation rows as JSON lines. Returns rows."""
    destination = Path(path)
    count = 0
    with destination.open("w", encoding="utf-8") as handle:
        for attempt, run in enumerate(runs, start=1):
            for row in run:
                handle.write(
                    json.dumps({"attempt": attempt, **row}, sort_keys=True, default=str)
                    + "\n"
                )
                count += 1
    return count


def write_record(record: dict[str, Any], out_path: str | Path) -> Path:
    """Write an AQR as JSON (``.json`` suffix) or YAML (otherwise).

    The SuperGauge schema allows no extra top-level keys, so ``x-*`` metadata
    (for example ``x-superoptix``) is split into a sidecar file
    (:func:`sidecar_path`) and the record itself stays schema-valid.
    """
    destination = Path(out_path)
    extensions = {k: v for k, v in record.items() if str(k).startswith("x-")}
    record = {k: v for k, v in record.items() if not str(k).startswith("x-")}
    if extensions:
        sidecar_path(destination).write_text(
            json.dumps(
                {"record_id": record.get("record_id"), **extensions},
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )
    if destination.suffix == ".json":
        destination.write_text(json.dumps(record, indent=2), encoding="utf-8")
    else:
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover
            raise ImportError("PyYAML is required to write YAML records") from exc
        destination.write_text(
            yaml.safe_dump(
                record, sort_keys=False, default_flow_style=False, width=100
            ),
            encoding="utf-8",
        )
    return destination


def _declared_tools(playbook: dict[str, Any]) -> list[str] | None:
    spec = playbook.get("spec") or playbook
    tools = spec.get("tools")
    if not isinstance(tools, list) or not tools:
        return None
    names = []
    for tool in tools:
        name = tool.get("name") if isinstance(tool, dict) else tool
        if name:
            names.append(str(name))
    return names or None


def assemble_record(
    *,
    agent_name: str,
    playbook_path: str | Path,
    playbook: dict[str, Any],
    scenarios: list[dict[str, Any]],
    runs: list[list[dict[str, Any]]],
    framework: str,
    tier: str = "T1",
    seal_requested: bool = False,
    holdout_record: dict[str, Any] | None = None,
    deterministic_gates: bool = False,
    floors: dict[str, float] | None = None,
    actor: str | None = None,
    checks_ignored: bool = False,
    ledger: str | None = None,
    ledger_events: int | None = None,
) -> dict[str, Any]:
    """Build an AQR from one or more evaluation runs (SuperOptiX 2.0).

    ``runs[0]`` is the primary evaluation; extra runs are independent repeats
    used only for ``reliability.pass_hat_k``. With ``seal_requested`` the
    sealed flag is derived from the GEPA held-out split (``holdout_record``),
    never asserted. With ``deterministic_gates`` the record carries gates on
    the deterministic measures the run produced and a deterministic decision.
    """
    from superoptix import gauge_checks as gc

    actor = gc.release_actor(actor)
    primary = list(runs[0]) if runs else []
    canaries = [r for r in primary if r.get("canary")]
    candidates = [r for r in primary if not r.get("canary")]

    seal = None
    if seal_requested:
        seal = gc.seal_holdout(scenarios, holdout_record)

    split = None
    evaluated = candidates
    if seal is not None and seal.sealed:
        wanted = set(seal.heldout_ids)
        evaluated = [r for r in candidates if r.get("sid") in wanted]
        split = "held-out"

    record = build_record(
        agent_name=agent_name,
        playbook_path=playbook_path,
        playbook=playbook,
        scenarios=[s for s in scenarios if not gc.is_canary(s)],
        results=evaluated,
        framework=framework,
        tier=tier,
        sealed=False,
        canary_ids=[str(r.get("name") or r.get("id")) for r in canaries] or None,
        actor=actor,
        ledger=ledger,
        ledger_format="superoptix.bdd-ledger/1",
        ledger_events=ledger_events,
    )
    # The ledger records outputs but cannot re-run the agent.
    record["assurance"]["evidence"]["replayable"] = False
    meta = record["x-superoptix"]
    if split:
        for m in record["measures"]:
            if m["id"] == "task.completion":
                m["split"] = split

    outcomes = gc.canary_outcomes(
        [{**r, "id": r.get("name") or r.get("id")} for r in canaries]
    )
    fired = [c for c in outcomes if c["observed"] != c["expected"]]
    if outcomes:
        record["assurance"]["integrity"] = {"canaries": outcomes}

    if seal is not None:
        task_set = record["task_set"]
        sealed = bool(seal.sealed and not fired)
        task_set["sealed"] = sealed
        task_set["held_in"] = seal.held_in
        task_set["held_out"] = seal.held_out
        if seal.digest and seal.sealed:
            task_set["manifest_digest"] = seal.digest
        reason = seal.reason
        if seal.sealed and fired:
            reason = "canary probe passed; split quarantined"
        meta["holdout"] = {"sealed": sealed, "reason": reason}
        if seal.digest:
            meta["holdout"]["split_digest"] = seal.digest
        record["measures"].append({"id": "assurance.holdout_sealed", "value": sealed})

    if deterministic_gates:
        if checks_ignored:
            meta["gates_note"] = "--ignore-checks was set; no gates recorded"
        else:
            spec = playbook.get("spec") or playbook
            contract = gc.declared_output_contract(spec)
            extra: list[dict[str, Any]] = []
            parse = gc.parse_rate_measure(evaluated, contract, split)
            if parse:
                extra.append(parse)
            scored = [r for r in evaluated if r.get("status") in {"passed", "failed"}]
            if scored and all(
                isinstance(r.get("baseline_passed"), bool)
                and r.get("success_condition") == scored[0].get("success_condition")
                for r in scored
            ):
                cand = sum(r["status"] == "passed" for r in scored) / len(scored)
                base = sum(r["baseline_passed"] for r in scored) / len(scored)
                extra.append(
                    gc.beats_baseline_measure(
                        candidate_value=cand,
                        baseline_value=base,
                        n=len(scored),
                        split=split,
                    )
                )
            ids = {r.get("id") for r in evaluated}
            repeats = [[r for r in run if r.get("id") in ids] for run in runs]
            extra.extend(gc.pass_hat_k_measures(repeats, split))
            tools = gc.tool_correctness_measure(
                evaluated, _declared_tools(playbook), split
            )
            if tools:
                extra.append(tools)
            trajectory = gc.trajectory_measure(evaluated, split)
            if trajectory:
                extra.append(trajectory)
            record["measures"].extend(extra)
            record["gates"] = gc.build_gates(record["measures"], floors)
        gc.decide(record, actor)
    return record
