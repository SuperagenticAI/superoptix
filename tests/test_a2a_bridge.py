"""Tests for 0.3 ↔ 1.0 negotiation.

The installed base is on 0.3: five of the eight adapted frameworks declare no
A2A at all, and the three that do are pinned pre-1.0. An endpoint that only
speaks 1.0 reaches almost none of the agents already deployed.
"""

from __future__ import annotations

import pytest

from superoptix.protocols.a2a import bridge


class TestVersionNormalisation:
    @pytest.mark.parametrize("value", ["1.0", "1.0.2", "1", ""])
    def test_one_line_spellings(self, value):
        assert bridge.normalize_version(value) == bridge.V1

    @pytest.mark.parametrize("value", ["0.3", "0.3.0", "0.3.25"])
    def test_zero_three_spellings(self, value):
        assert bridge.normalize_version(value) == bridge.V03

    @pytest.mark.parametrize("value", ["99.0", "0.2", "2.0", "nonsense"])
    def test_unknown_lines_are_rejected(self, value):
        """Mapping anything unknown onto 0.3 would silently accept '99.0'."""
        assert bridge.normalize_version(value) is None


class TestTaskTranslation:
    def _task(self):
        return {
            "id": "t1",
            "status": {
                "state": "TASK_STATE_COMPLETED",
                "message": {"role": "ROLE_AGENT", "parts": [{"text": "hi"}]},
            },
            "history": [{"role": "ROLE_USER", "parts": [{"text": "hello"}]}],
        }

    def test_states_are_downgraded(self):
        assert bridge.task_to_v03(self._task())["status"]["state"] == "completed"

    def test_roles_are_downgraded(self):
        out = bridge.task_to_v03(self._task())
        assert out["status"]["message"]["role"] == "agent"
        assert out["history"][0]["role"] == "user"

    def test_parts_regain_their_0_3_wrapper(self):
        """1.0 unified Part; 0.3 tagged each with `kind`."""
        part = bridge.task_to_v03(self._task())["status"]["message"]["parts"][0]
        assert part == {"kind": "text", "text": "hi"}

    def test_round_trip_is_stable(self):
        original = self._task()
        assert bridge.task_to_v1(bridge.task_to_v03(original)) == original

    def test_file_parts_translate_both_ways(self):
        one = {
            "id": "t",
            "artifacts": [
                {
                    "artifactId": "a",
                    "parts": [
                        {"filename": "r.txt", "mediaType": "text/plain", "raw": "Zm8="}
                    ],
                }
            ],
        }
        legacy = bridge.task_to_v03(one)
        file_part = legacy["artifacts"][0]["parts"][0]
        assert file_part["kind"] == "file"
        assert file_part["file"]["name"] == "r.txt"
        assert file_part["file"]["bytes"] == "Zm8="
        assert bridge.task_to_v1(legacy) == one

    def test_an_empty_task_survives(self):
        assert bridge.task_to_v03({}) == {}


class TestCardTranslation:
    def _card(self):
        return {
            "name": "A",
            "protocolVersion": "1.0",
            "supportedInterfaces": [
                {"url": "https://x/rpc", "protocolBinding": "JSONRPC", "protocolVersion": "1.0"},
                {"url": "https://x", "protocolBinding": "HTTP+JSON", "protocolVersion": "1.0"},
                {"url": "https://x/rpc", "protocolBinding": "JSONRPC", "protocolVersion": "0.3"},
            ],
        }

    def test_legacy_card_declares_the_0_3_line(self):
        assert bridge.card_to_v03(self._card())["protocolVersion"] == "0.3"

    def test_legacy_card_gets_a_top_level_url(self):
        """A 0.3 reader has nothing to call without one."""
        assert bridge.card_to_v03(self._card())["url"] == "https://x/rpc"

    def test_prefers_an_interface_advertised_on_the_0_3_line(self):
        card = bridge.card_to_v03(self._card())
        assert card["preferredTransport"] == "JSONRPC"


class TestNegotiationOverHttp:
    @pytest.fixture()
    def client(self):
        testclient = pytest.importorskip("fastapi.testclient")
        from superoptix.protocols.a2a.public.app import create_public_app

        return testclient.TestClient(create_public_app("http://testserver"))

    def _send(self, client, version):
        return client.post(
            "/message:send",
            json={"message": {"role": "ROLE_USER", "parts": [{"text": "does dspy support a2a"}]}},
            headers={"A2A-Version": version},
        ).json()["task"]

    def test_a_1_0_caller_gets_the_1_0_shape(self, client):
        task = self._send(client, "1.0")
        assert task["status"]["state"] == "TASK_STATE_COMPLETED"
        assert task["status"]["message"]["role"] == "ROLE_AGENT"

    def test_a_0_3_caller_gets_the_0_3_shape(self, client):
        task = self._send(client, "0.3")
        assert task["status"]["state"] == "completed"
        assert task["status"]["message"]["role"] == "agent"
        assert task["status"]["message"]["parts"][0]["kind"] == "text"

    def test_the_card_is_negotiated_too(self, client):
        one = client.get("/.well-known/agent-card.json", headers={"A2A-Version": "1.0"})
        legacy = client.get("/.well-known/agent-card.json", headers={"A2A-Version": "0.3"})
        assert one.json()["protocolVersion"] == "1.0"
        assert legacy.json()["protocolVersion"] == "0.3"

    def test_an_unsupported_version_is_still_refused(self, client):
        from superoptix.protocols.a2a import errors as a2a_errors

        response = client.get("/tasks", headers={"A2A-Version": "99.0"})
        assert response.status_code == a2a_errors.VERSION_NOT_SUPPORTED.http_status

    def test_jsonrpc_message_send_uses_the_0_3_shape(self, client):
        body = client.post(
            "/a2a/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "id": "1",
                "method": "message/send",
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [{"kind": "text", "text": "does dspy support a2a"}],
                    }
                },
            },
        ).json()
        task = body["result"]
        assert task["status"]["state"] == "completed"
        assert task["status"]["message"]["role"] == "agent"
        assert task["status"]["message"]["parts"][0]["kind"] == "text"

    def test_jsonrpc_send_with_version_header_translates_too(self, client):
        body = client.post(
            "/a2a/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "id": "1",
                "method": "SendMessage",
                "params": {
                    "message": {"role": "ROLE_USER", "parts": [{"text": "hi"}]}
                },
            },
            headers={"A2A-Version": "0.3"},
        ).json()
        task = body["result"]
        assert task["status"]["state"] == "completed"
        assert "task" not in task
