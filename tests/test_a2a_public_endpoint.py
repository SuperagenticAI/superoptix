"""Tests for the published public A2A endpoint and its catalogue skills."""

from __future__ import annotations

import json

import pytest

from superoptix.protocols.a2a.public import (
    FRAMEWORK_A2A_STATUS,
    PUBLIC_SKILL_DEFINITIONS,
    agent_card_review,
    build_public_agent_card,
    framework_a2a_readiness,
)


class TestFrameworkReadinessSkill:
    def test_names_a_single_framework_when_asked(self):
        result = framework_a2a_readiness("Does CrewAI support A2A?")
        frameworks = result["data"]["frameworks"]
        assert [f["framework"] for f in frameworks] == ["crewai"]
        assert frameworks[0]["spec_line"] == "0.3"

    def test_lists_every_framework_when_unspecified(self):
        result = framework_a2a_readiness("which frameworks support a2a")
        assert len(result["data"]["frameworks"]) == len(FRAMEWORK_A2A_STATUS)

    def test_reports_frameworks_with_no_a2a_support(self):
        result = framework_a2a_readiness("dspy")
        row = result["data"]["frameworks"][0]
        assert row["a2a_support"] == "none"
        assert row["declares"] is None

    def test_resolves_aliases(self):
        result = framework_a2a_readiness("what about adk")
        assert result["data"]["frameworks"][0]["framework"] == "google-adk"

    def test_no_framework_claims_native_1_0(self):
        """The core selling point: none of the eight reach A2A 1.0 alone."""
        for info in FRAMEWORK_A2A_STATUS.values():
            assert info["spec_line"] != "1.0"


class TestAgentCardReviewSkill:
    def test_explains_itself_without_a_card(self):
        result = agent_card_review("how do I use this?")
        assert result["data"]["reviewed"] is False

    def test_flags_missing_1_0_fields(self):
        result = agent_card_review(json.dumps({"name": "bare", "skills": []}))
        fields = {f["field"] for f in result["data"]["findings"]}
        assert {"protocolVersion", "signature", "skills"} <= fields
        assert result["data"]["score"] < 60

    def test_flags_pre_1_0_protocol_version(self):
        card = {"name": "old", "protocolVersion": "0.3", "skills": []}
        findings = agent_card_review(json.dumps(card))["data"]["findings"]
        assert any(
            f["field"] == "protocolVersion" and "0.3" in f["issue"] for f in findings
        )

    def test_flags_vague_and_undocumented_skills(self):
        card = {
            "name": "x",
            "skills": [{"id": "s", "description": "agent"}],
        }
        fields = {f["field"] for f in agent_card_review(json.dumps(card))["data"]["findings"]}
        assert "skills.s.description" in fields
        assert "skills.s.examples" in fields

    def test_findings_are_ordered_by_severity(self):
        findings = agent_card_review(json.dumps({"name": "x"}))["data"]["findings"]
        order = {"high": 0, "medium": 1, "low": 2}
        assert [order[f["severity"]] for f in findings] == sorted(
            order[f["severity"]] for f in findings
        )


class TestPublicAgentCard:
    def test_advertises_both_spec_lines(self):
        """A 1.0 card that also advertises 0.3 so pre-1.0 clients negotiate."""
        card = build_public_agent_card()
        versions = {i["protocolVersion"] for i in card["supportedInterfaces"]}
        assert versions == {"1.0", "0.3"}
        assert card["protocolVersion"] == "1.0"

    def test_advertises_both_bindings(self):
        card = build_public_agent_card()
        bindings = {i["protocolBinding"] for i in card["supportedInterfaces"]}
        assert bindings == {"JSONRPC", "HTTP+JSON"}
        assert card["preferredTransport"] == "JSONRPC"

    def test_declares_security_and_provenance_fields(self):
        card = build_public_agent_card()
        assert card["securitySchemes"]["bearer"]["scheme"] == "bearer"
        assert card["provider"]["organization"] == "Superagentic AI"
        assert card["documentationUrl"]

    def test_skills_match_the_served_definitions(self):
        card = build_public_agent_card()
        assert [s["id"] for s in card["skills"]] == [
            s["id"] for s in PUBLIC_SKILL_DEFINITIONS
        ]

    def test_honours_the_deployed_service_url(self):
        card = build_public_agent_card(service_url="https://a2a.superoptix.ai")
        assert card["url"] == "https://a2a.superoptix.ai"
        assert all(
            i["url"].startswith("https://a2a.superoptix.ai")
            for i in card["supportedInterfaces"]
        )

    def test_our_own_card_passes_our_own_review(self):
        """Only the unsigned-card finding should remain; see roadmap item C3."""
        review = agent_card_review(json.dumps(build_public_agent_card()))
        fields = [f["field"] for f in review["data"]["findings"]]
        assert fields == ["signature"]
        assert review["data"]["score"] >= 85


class TestPublicEndpoint:
    @pytest.fixture()
    def client(self):
        fastapi_testclient = pytest.importorskip("fastapi.testclient")
        from superoptix.protocols.a2a.public.app import create_public_app

        return fastapi_testclient.TestClient(create_public_app("https://example.test"))

    def test_serves_the_card_at_the_well_known_path(self, client):
        response = client.get("/.well-known/agent-card.json")
        assert response.status_code == 200
        assert response.json()["name"] == "SuperOptiX"

    def test_answers_a_message_send_call(self, client):
        response = client.post(
            "/message:send",
            json={
                "message": {
                    "role": "ROLE_USER",
                    "parts": [{"text": "Does CrewAI support A2A?"}],
                }
            },
        )
        assert response.status_code == 200
        body = json.dumps(response.json())
        assert "CrewAI" in body
        # Routed to the readiness skill and answered about the framework asked for.
        assert "Agent Card review" not in body

    def test_routes_a_json_card_to_the_review_skill(self, client):
        response = client.post(
            "/message:send",
            json={
                "message": {
                    "role": "ROLE_USER",
                    "parts": [{"text": '{"name": "probe", "skills": []}'}],
                }
            },
        )
        assert response.status_code == 200
        assert "Agent Card review" in json.dumps(response.json())
