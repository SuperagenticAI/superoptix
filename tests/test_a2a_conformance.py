"""Regression tests for A2A 1.0 conformance behaviours.

Each test here corresponds to a requirement the official A2A TCK checks. They
exist so a conformance fix cannot be silently undone between TCK runs.
"""

from __future__ import annotations

import pytest

from superoptix.protocols.a2a import errors as a2a_errors

RPC = "/a2a/jsonrpc"
SPEC_TASK_FIELDS = {"id", "contextId", "status", "artifacts", "history", "metadata"}


@pytest.fixture()
def client():
    fastapi_testclient = pytest.importorskip("fastapi.testclient")
    from superoptix.protocols.a2a.public.app import create_public_app

    return fastapi_testclient.TestClient(create_public_app("http://testserver"))


def _new_task(client) -> dict:
    response = client.post(
        "/message:send",
        json={"message": {"role": "ROLE_USER", "parts": [{"text": "hi"}]}},
    )
    assert response.status_code == 200
    body = response.json()
    return body.get("task", body)


class TestTaskSchema:
    def test_task_carries_only_spec_fields(self, client):
        """The A2A Task schema sets additionalProperties: false."""
        task = _new_task(client)
        assert set(task) <= SPEC_TASK_FIELDS, (
            f"non-spec fields: {set(task) - SPEC_TASK_FIELDS}"
        )

    def test_status_carries_the_timestamp(self, client):
        """Timestamps belong on status, not on the Task."""
        task = _new_task(client)
        assert task["status"]["timestamp"]


class TestJsonRpcErrors:
    def test_errors_return_http_200(self, client):
        """JSON-RPC failures ride inside the envelope; the transport succeeded."""
        response = client.post(
            RPC,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "GetTask",
                "params": {"id": "nope"},
            },
        )
        assert response.status_code == 200
        assert (
            response.json()["error"]["code"] == a2a_errors.TASK_NOT_FOUND.jsonrpc_code
        )

    def test_a2a_errors_carry_errorinfo_in_a_data_array(self, client):
        """Spec section 9.5: error.data is a ProtoJSON array holding ErrorInfo."""
        response = client.post(
            RPC,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "GetTask",
                "params": {"id": "nope"},
            },
        )
        data = response.json()["error"]["data"]
        assert isinstance(data, list)
        info = next(i for i in data if i.get("@type") == a2a_errors.ERRORINFO_TYPE)
        assert info["domain"] == a2a_errors.ERROR_DOMAIN
        assert info["reason"] == "TASK_NOT_FOUND"

    def test_trailing_slash_is_served(self, client):
        """A client using the interface URL as a base and posting "/" lands here.

        Without this route Starlette answers with an empty 307 body, which
        JSON-RPC clients cannot parse.
        """
        response = client.post(
            RPC + "/",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "GetTask",
                "params": {"id": "nope"},
            },
        )
        assert response.status_code == 200
        assert (
            response.json()["error"]["code"] == a2a_errors.TASK_NOT_FOUND.jsonrpc_code
        )

    def test_malformed_envelope_is_rejected(self, client):
        response = client.post(RPC, json={"jsonrpc": "2.0", "id": 1})
        assert (
            response.json()["error"]["code"] == a2a_errors.INVALID_REQUEST.jsonrpc_code
        )

    def test_unknown_method_is_method_not_found(self, client):
        response = client.post(
            RPC,
            json={"jsonrpc": "2.0", "id": 1, "method": "NoSuchMethod", "params": {}},
        )
        assert (
            response.json()["error"]["code"] == a2a_errors.METHOD_NOT_FOUND.jsonrpc_code
        )

    @pytest.mark.parametrize(
        "method",
        [
            "CreateTaskPushNotificationConfig",
            "GetTaskPushNotificationConfig",
            "ListTaskPushNotificationConfigs",
            "DeleteTaskPushNotificationConfig",
        ],
    )
    def test_push_notification_methods_report_unsupported(self, client, method):
        """The card declares pushNotifications: false, so this is the spec'd answer."""
        response = client.post(
            RPC, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": {}}
        )
        code = response.json()["error"]["code"]
        assert code == a2a_errors.PUSH_NOTIFICATION_NOT_SUPPORTED.jsonrpc_code


class TestVersionNegotiation:
    def test_unsupported_version_is_rejected_over_jsonrpc(self, client):
        response = client.post(
            RPC,
            json={"jsonrpc": "2.0", "id": 1, "method": "ListTasks", "params": {}},
            headers={"A2A-Version": "99.0"},
        )
        assert (
            response.json()["error"]["code"]
            == a2a_errors.VERSION_NOT_SUPPORTED.jsonrpc_code
        )

    @pytest.mark.parametrize("version", ["1.0", "0.3"])
    def test_advertised_versions_are_accepted(self, client, version):
        response = client.post(
            RPC,
            json={"jsonrpc": "2.0", "id": 1, "method": "ListTasks", "params": {}},
            headers={"A2A-Version": version},
        )
        assert "error" not in response.json()


class TestHttpJsonBinding:
    def test_unknown_task_is_404_with_an_aip193_body(self, client):
        response = client.get("/tasks/does-not-exist")
        assert response.status_code == a2a_errors.TASK_NOT_FOUND.http_status
        error = response.json()["error"]
        assert error["status"] == "TASK_NOT_FOUND"
        assert any(
            d.get("@type") == a2a_errors.ERRORINFO_TYPE for d in error["details"]
        )

    def test_unsupported_content_type_is_415(self, client):
        """FastAPI would otherwise answer its own 422 validation error."""
        response = client.post(
            "/message:send", content="not json", headers={"content-type": "text/plain"}
        )
        assert response.status_code == a2a_errors.CONTENT_TYPE_NOT_SUPPORTED.http_status

    def test_cancelling_a_terminal_task_is_an_error(self, client):
        task = _new_task(client)
        assert task["status"]["state"] == "TASK_STATE_COMPLETED"
        response = client.post(f"/tasks/{task['id']}:cancel")
        assert response.status_code == a2a_errors.TASK_NOT_CANCELABLE.http_status


class TestTaskSemantics:
    """Behaviours the TCK checks that are easy to regress."""

    def test_follow_up_continues_the_same_task(self, client):
        """A message carrying taskId extends that task, it does not fork one."""
        first = _new_task(client)
        response = client.post(
            "/message:send",
            json={
                "message": {
                    "role": "ROLE_USER",
                    "parts": [{"text": "follow up"}],
                    "taskId": first["id"],
                }
            },
        )
        # The task is terminal, so a follow-up is refused rather than forked.
        assert response.status_code == a2a_errors.UNSUPPORTED_OPERATION.http_status

    def test_unknown_task_reference_is_rejected(self, client):
        response = client.post(
            "/message:send",
            json={
                "message": {
                    "role": "ROLE_USER",
                    "parts": [{"text": "hi"}],
                    "taskId": "no-such-task",
                }
            },
        )
        assert response.status_code == a2a_errors.TASK_NOT_FOUND.http_status

    def test_mismatched_context_is_rejected(self, client):
        task = _new_task(client)
        response = client.post(
            "/message:send",
            json={
                "message": {
                    "role": "ROLE_USER",
                    "parts": [{"text": "hi"}],
                    "taskId": task["id"],
                    "contextId": "a-different-context",
                }
            },
        )
        assert response.status_code == a2a_errors.INVALID_PARAMS.http_status

    def test_empty_message_is_rejected(self, client):
        response = client.post("/message:send", json={"message": {"role": "ROLE_USER"}})
        assert response.status_code == a2a_errors.INVALID_PARAMS.http_status

    def test_history_length_truncates(self, client):
        task = _new_task(client)
        response = client.get(f"/tasks/{task['id']}", params={"historyLength": 1})
        assert len(response.json()["history"]) <= 1


class TestSutHarness:
    """The conformance harness stays separate from the published agent."""

    def test_public_runtime_ignores_tck_scenario_prefixes(self, client):
        """A production agent must not change behaviour on client-supplied ids."""
        response = client.post(
            "/message:send",
            json={
                "message": {
                    "role": "ROLE_USER",
                    "messageId": "tck-input-required-1",
                    "parts": [{"text": "hi"}],
                }
            },
        )
        task = response.json()["task"]
        assert task["status"]["state"] == "TASK_STATE_COMPLETED"

    def test_sut_harness_honours_them(self):
        fastapi_testclient = pytest.importorskip("fastapi.testclient")
        from superoptix.protocols.a2a.tck_sut import create_sut_app

        sut = fastapi_testclient.TestClient(create_sut_app("http://testserver"))
        response = sut.post(
            "/message:send",
            json={
                "message": {
                    "role": "ROLE_USER",
                    "messageId": "tck-input-required-1",
                    "parts": [{"text": "hi"}],
                }
            },
        )
        task = response.json()["task"]
        assert task["status"]["state"] == "TASK_STATE_INPUT_REQUIRED"

    def test_sut_harness_returns_a_bare_message_when_asked(self):
        fastapi_testclient = pytest.importorskip("fastapi.testclient")
        from superoptix.protocols.a2a.tck_sut import create_sut_app

        sut = fastapi_testclient.TestClient(create_sut_app("http://testserver"))
        response = sut.post(
            "/message:send",
            json={
                "message": {
                    "role": "ROLE_USER",
                    "messageId": "tck-message-response-1",
                    "parts": [{"text": "hi"}],
                }
            },
        )
        body = response.json()
        assert "message" in body and "task" not in body
        assert body["message"]["parts"][0]["text"] == "Direct message response"


class TestErrorBindings:
    def test_every_a2a_error_declares_an_errorinfo_reason(self):
        for error in a2a_errors.ALL_ERRORS.values():
            if error.jsonrpc_code > -32100:  # A2A-specific range
                assert error.reason, f"{error.name} has no ErrorInfo reason"

    def test_standard_jsonrpc_errors_carry_no_errorinfo(self):
        assert a2a_errors.METHOD_NOT_FOUND.details() == []
        assert a2a_errors.INVALID_REQUEST.details() == []


class TestAgentCardCaching:
    """CARD-CACHE-001/002/003: the card is served with cache validators."""

    CARD = "/.well-known/agent-card.json"

    def test_cache_control_declares_max_age(self, client):
        headers = client.get(self.CARD).headers
        assert "max-age" in headers["cache-control"]

    def test_etag_and_last_modified_are_present(self, client):
        headers = client.get(self.CARD).headers
        assert headers["etag"].startswith('"')
        assert headers["last-modified"]

    def test_vary_names_the_negotiating_header(self, client):
        """The two renderings differ, so a cache has to key on the header."""
        assert client.get(self.CARD).headers["vary"] == "A2A-Version"

    def test_matching_etag_returns_304(self, client):
        etag = client.get(self.CARD).headers["etag"]
        response = client.get(self.CARD, headers={"If-None-Match": etag})
        assert response.status_code == 304
        assert not response.content

    def test_wildcard_matches(self, client):
        assert client.get(self.CARD, headers={"If-None-Match": "*"}).status_code == 304

    def test_weak_validator_matches_its_strong_form(self, client):
        etag = client.get(self.CARD).headers["etag"]
        response = client.get(self.CARD, headers={"If-None-Match": f"W/{etag}"})
        assert response.status_code == 304

    def test_stale_etag_returns_the_card(self, client):
        response = client.get(self.CARD, headers={"If-None-Match": '"stale"'})
        assert response.status_code == 200

    def test_the_two_spec_lines_carry_different_etags(self, client):
        current = client.get(self.CARD).headers["etag"]
        legacy = client.get(self.CARD, headers={"A2A-Version": "0.3"}).headers["etag"]
        assert current != legacy

    def test_an_etag_from_one_version_does_not_match_the_other(self, client):
        legacy = client.get(self.CARD, headers={"A2A-Version": "0.3"}).headers["etag"]
        response = client.get(self.CARD, headers={"If-None-Match": legacy})
        assert response.status_code == 200


class TestLegacyMethodNames:
    """The card advertises a 0.3 JSON-RPC interface, so 0.3 names must work."""

    def _call(self, client, method, params, headers=None):
        return client.post(
            RPC,
            json={"jsonrpc": "2.0", "id": "1", "method": method, "params": params},
            headers=headers or {},
        ).json()

    def test_message_send_reaches_the_handler(self, client):
        body = self._call(
            client,
            "message/send",
            {"message": {"role": "user", "messageId": "m1", "parts": [{"kind": "text", "text": "hi"}]}},
        )
        assert "error" not in body, body
        task = body["result"]
        assert task["status"]["state"] == "completed"
        assert task["status"]["message"]["role"] == "agent"
        assert "task" not in task

    def test_one_line_send_still_wraps_the_task(self, client):
        body = self._call(
            client,
            "SendMessage",
            {"message": {"role": "ROLE_USER", "parts": [{"text": "hi"}]}},
        )
        assert "error" not in body, body
        task = body["result"]["task"]
        assert task["status"]["state"] == "TASK_STATE_COMPLETED"

    def test_tasks_get_reports_a_missing_task(self, client):
        body = self._call(client, "tasks/get", {"id": "missing"})
        assert body["error"]["code"] == a2a_errors.TASK_NOT_FOUND.jsonrpc_code

    def test_tasks_get_accepts_a_resource_name(self, client):
        body = self._call(client, "tasks/get", {"name": "tasks/nope"})
        assert body["error"]["code"] == a2a_errors.TASK_NOT_FOUND.jsonrpc_code

    def test_tasks_get_returns_a_real_task(self, client):
        sent = self._call(
            client,
            "message/send",
            {"message": {"role": "user", "parts": [{"kind": "text", "text": "hi"}]}},
        )
        task_id = sent["result"]["id"]
        body = self._call(client, "tasks/get", {"id": task_id})
        assert "error" not in body, body
        assert body["result"]["id"] == task_id
        assert body["result"]["status"]["state"] == "completed"

    def test_tasks_cancel_reports_a_missing_task(self, client):
        body = self._call(client, "tasks/cancel", {"id": "missing"})
        assert body["error"]["code"] == a2a_errors.TASK_NOT_FOUND.jsonrpc_code

    def test_extended_card_reports_it_is_unsupported(self, client):
        """CORE-CAP-003: the card declares extendedAgentCard false."""
        body = self._call(client, "agent/authenticatedExtendedCard", {})
        assert body["error"]["code"] == a2a_errors.UNSUPPORTED_OPERATION.jsonrpc_code

    def test_push_config_reports_it_is_unsupported(self, client):
        body = self._call(client, "tasks/pushNotificationConfig/set", {})
        assert body["error"]["code"] == a2a_errors.PUSH_NOTIFICATION_NOT_SUPPORTED.jsonrpc_code

    def test_the_1_0_names_still_work(self, client):
        body = self._call(client, "GetTask", {"id": "missing"})
        assert body["error"]["code"] == a2a_errors.TASK_NOT_FOUND.jsonrpc_code

    def test_an_unknown_method_is_still_rejected(self, client):
        body = self._call(client, "bogus/thing", {})
        assert body["error"]["code"] == a2a_errors.METHOD_NOT_FOUND.jsonrpc_code

    def test_empty_stream_parts_are_rejected(self, client):
        body = self._call(
            client,
            "message/stream",
            {"message": {"role": "user", "parts": []}},
        )
        assert body["error"]["code"] == a2a_errors.INVALID_PARAMS.jsonrpc_code


class TestSendMessageHistoryLength:
    """CORE-HIST-003: SendMessage honours configuration.historyLength."""

    def _send(self, client, text, context_id=None, history_length=None):
        message = {"role": "ROLE_USER", "parts": [{"text": text}]}
        if context_id:
            message["contextId"] = context_id
        body = {"message": message}
        if history_length is not None:
            body["configuration"] = {"historyLength": history_length}
        return client.post("/message:send", json=body).json()["task"]

    @pytest.fixture()
    def context(self, client):
        """A context carrying enough turns for a cap to be observable."""
        first = self._send(client, "first")
        context_id = first["contextId"]
        for text in ("second", "third", "fourth"):
            self._send(client, text, context_id)
        return context_id

    def test_zero_returns_no_history(self, client, context):
        """Zero is a value, not an absent field."""
        task = self._send(client, "next", context, history_length=0)
        assert task["history"] == []

    def test_a_cap_keeps_the_most_recent_messages(self, client, context):
        task = self._send(client, "next", context, history_length=1)
        assert len(task["history"]) == 1

    def test_an_absent_cap_leaves_history_alone(self, client, context):
        capped = self._send(client, "next", context, history_length=0)
        uncapped = self._send(client, "next", context)
        assert len(uncapped["history"]) > len(capped["history"])

    def test_a_negative_cap_is_ignored(self, client, context):
        task = self._send(client, "next", context, history_length=-1)
        assert task["history"]


class TestSpecMandatedErrorCodes:
    """The TCK asserts the specific error, not merely that one was returned."""

    def _terminal_task(self, client):
        body = client.post(
            "/message:send",
            json={"message": {"role": "ROLE_USER", "parts": [{"text": "hi"}]}},
        ).json()
        return body["task"]["id"]

    def test_subscribe_to_terminal_task_is_unsupported_over_jsonrpc(self, client):
        """STREAM-SUB-003, spec 3.1.6."""
        task_id = self._terminal_task(client)
        body = client.post(
            RPC,
            json={
                "jsonrpc": "2.0",
                "id": "1",
                "method": "SubscribeToTask",
                "params": {"id": task_id},
            },
        ).json()
        assert body["error"]["code"] == a2a_errors.UNSUPPORTED_OPERATION.jsonrpc_code

    def test_subscribe_to_terminal_task_is_unsupported_over_http(self, client):
        """The REST binding must agree with the JSON-RPC one."""
        task_id = self._terminal_task(client)
        response = client.post(f"/tasks/{task_id}:subscribe")
        assert response.status_code == a2a_errors.UNSUPPORTED_OPERATION.http_status

    def test_cancel_still_reports_task_not_cancelable(self, client):
        """TaskNotCancelable belongs to CancelTask, and must not leak to subscribe."""
        task_id = self._terminal_task(client)
        body = client.post(
            RPC,
            json={
                "jsonrpc": "2.0",
                "id": "1",
                "method": "CancelTask",
                "params": {"id": task_id},
            },
        ).json()
        assert body["error"]["code"] == a2a_errors.TASK_NOT_CANCELABLE.jsonrpc_code

    def test_extended_card_is_unsupported_over_http(self, client):
        """CORE-CAP-003 on the REST binding."""
        response = client.get("/extendedAgentCard")
        assert response.status_code == a2a_errors.UNSUPPORTED_OPERATION.http_status
