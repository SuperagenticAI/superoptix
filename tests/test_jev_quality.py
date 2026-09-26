"""Unit tests for optional Jev / System One quality-control (no typesafe required)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from superoptix.gauge import apply_jev_judgment, build_record, write_record
from superoptix.quality.admission import admit_proposal
from superoptix.quality.jev import (
    CHOICE_TO_VERDICT,
    DispositionJudgment,
    ThresholdVersion,
    choice_to_verdict,
    digest_pack_bytes,
    heuristic_disposition_from_evaluate,
    heuristic_disposition_from_findings,
    pin_assurance_judge,
    resolve_verdict,
    typesafe_available,
)


def test_choice_to_verdict_mapping():
    assert CHOICE_TO_VERDICT == {
        "accept": "ship",
        "warn": "hold",
        "reject": "reject",
    }
    assert choice_to_verdict("accept") == "ship"
    assert choice_to_verdict("WARN") == "hold"
    assert choice_to_verdict("reject") == "reject"
    with pytest.raises(ValueError):
        choice_to_verdict("maybe")


def test_soft_hold_on_low_confidence():
    verdict, rationale = resolve_verdict("accept", 0.41, min_confidence=0.75)
    assert verdict == "hold"
    assert rationale is not None
    assert "Soft-hold" in rationale
    assert "0.41" in rationale

    verdict_ok, rationale_ok = resolve_verdict("accept", 0.92, min_confidence=0.75)
    assert verdict_ok == "ship"
    assert rationale_ok is None

    # warn / reject are unaffected by confidence soft-hold
    assert resolve_verdict("warn", 0.99)[0] == "hold"
    assert resolve_verdict("reject", 0.99)[0] == "reject"


def test_pin_assurance_judge():
    assurance = pin_assurance_judge(
        {"evaluator_independent": False},
        model="jev-1.13.0",
        pack_digest="sha256:" + "ab" * 32,
        human_agreement_kappa=0.71,
        sampled=40,
        calibration_ece=0.08,
    )
    judge = assurance["judge"]
    assert judge["id"] == "typesafe/jev@1"
    assert judge["model"] == "jev-1.13.0"
    assert judge["pack_digest"].startswith("sha256:")
    assert judge["human_agreement_kappa"] == 0.71
    assert judge["sampled"] == 40
    assert judge["calibration_ece"] == 0.08


def test_apply_jev_judgment_soft_hold_sample(tmp_path: Path):
    playbook = tmp_path / "agent_playbook.yaml"
    playbook.write_text("spec:\n  tools: []\n", encoding="utf-8")
    record = build_record(
        agent_name="demo",
        playbook_path=playbook,
        playbook={"spec": {"tools": []}},
        scenarios=[{"name": "a", "split": "held-out"}],
        results=[{"id": "a", "status": "passed"}],
        framework="dspy",
    )
    judgment = DispositionJudgment(
        choice="accept",
        confidence=0.41,
        model="jev-1.13.0",
        pack_digest=digest_pack_bytes({"id": "pack@1"}),
        rationale="Unit test judgment.",
        source="test",
    )
    apply_jev_judgment(
        record,
        judgment,
        min_confidence=0.75,
        threshold_version=ThresholdVersion(version="reanchor-test.1").to_dict(),
    )

    assert record["decision"]["verdict"] == "hold"
    assert "Soft-hold" in record["decision"]["rationale"]
    assert record["assurance"]["judge"]["model"] == "jev-1.13.0"
    assert record["assurance"]["judge"]["pack_digest"].startswith("sha256:")
    # No confidence gate invented
    assert record["gates"] == []
    assert "confidence" not in json.dumps(record["gates"])
    jev_meta = record["x-superoptix"]["jev"]
    assert jev_meta["disposition"]["choice"] == "accept"
    assert jev_meta["threshold_version"]["version"] == "reanchor-test.1"

    out = write_record(record, tmp_path / "aqr.json")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["decision"]["verdict"] == "hold"
    assert loaded["assurance"]["judge"]["model"] == "jev-1.13.0"


def test_heuristic_evaluate_and_card_review():
    accept = heuristic_disposition_from_evaluate(passed=10, total=10)
    assert accept.choice == "accept"
    reject = heuristic_disposition_from_evaluate(passed=1, total=10)
    assert reject.choice == "reject"
    warn = heuristic_disposition_from_evaluate(passed=6, total=10)
    assert warn.choice == "warn"

    card = heuristic_disposition_from_findings(
        score=88,
        findings=[{"severity": "low", "field": "tags", "issue": "missing"}],
    )
    assert card.choice == "accept"
    card_warn = heuristic_disposition_from_findings(
        score=70,
        findings=[
            {"severity": "medium", "field": "securitySchemes", "issue": "absent"}
        ],
    )
    assert card_warn.choice == "warn"
    card_reject = heuristic_disposition_from_findings(
        score=40,
        findings=[{"severity": "high", "field": "skills", "issue": "none"}],
    )
    assert card_reject.choice == "reject"


def test_admit_proposal_propose_dont_judge():
    held = admit_proposal(
        referee=DispositionJudgment(choice="accept", confidence=0.4, source="test")
    )
    assert held.action == "hold"
    assert held.verdict == "hold"

    admitted = admit_proposal(
        referee={"choice": "accept", "confidence": 0.9},
    )
    assert admitted.action == "admit"
    assert admitted.verdict == "ship"

    rejected = admit_proposal(
        referee=DispositionJudgment(choice="reject", confidence=0.95, source="test")
    )
    assert rejected.action == "reject"

    metric_path = admit_proposal(metric_value=0.9, metric_floor=0.8)
    assert metric_path.action == "admit"


def test_typesafe_available_is_bool():
    assert isinstance(typesafe_available(), bool)


@pytest.mark.typesafe
def test_typesafe_adapter_imports_when_extra_present():
    if not typesafe_available():
        pytest.skip("dspy[typesafe] not installed")
    from superoptix.quality.typesafe_adapter import (
        make_typesafe_lm,
        release_disposition_type,
    )

    Disposition = release_disposition_type()
    assert Disposition is not None
    lm = make_typesafe_lm("jev-1.13.0")
    assert getattr(lm, "model", None) == "jev-1.13.0"


def test_card_review_includes_disposition():
    from superoptix.protocols.a2a.public.skills import agent_card_review

    card = {
        "protocolVersion": "1.0",
        "name": "demo",
        "description": "A carefully described demo agent for routing tests.",
        "signature": {"protected": "x"},
        "securitySchemes": {"apiKey": {}},
        "supportedInterfaces": [
            {"protocolBinding": "JSONRPC", "protocolVersion": "1.0"},
            {"protocolBinding": "HTTP+JSON", "protocolVersion": "1.0"},
        ],
        "skills": [
            {
                "id": "demo",
                "description": "Demonstrates a clear, specific skill for callers to route on.",
                "examples": ["do the demo thing"],
                "tags": ["demo"],
            }
        ],
        "provider": {"organization": "Acme"},
        "documentationUrl": "https://example.com",
        "preferredTransport": "JSONRPC",
    }
    result = agent_card_review(json.dumps(card))
    assert result["data"]["reviewed"] is True
    assert "disposition" in result["data"]
    assert result["data"]["disposition"]["choice"] in {"accept", "warn", "reject"}
