"""A2A client keep-alive session and interface selection (2.0)."""

from unittest import mock

import superoptix  # noqa: F401  (import superoptix before dspy)
from superoptix.protocols.a2a.client import A2AClient
from superoptix.protocols.a2a.registry import A2ARegistry

CARD_URL = "http://peer.example/.well-known/agent-card.json"


def _card(interfaces):
    return {
        "name": "peer",
        "description": "d",
        "version": "1",
        "supportedInterfaces": interfaces,
        "skills": [],
    }


def _response(payload):
    resp = mock.Mock()
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp


def test_one_session_reused_across_requests():
    client = A2AClient(agent_url="http://peer.example")
    card = _card(
        [
            {
                "url": "http://peer.example",
                "protocolBinding": "HTTP+JSON",
                "protocolVersion": "1.0",
            }
        ]
    )
    task = {"task": {"id": "t1", "status": {"state": "TASK_STATE_COMPLETED"}}}
    with mock.patch("requests.Session.request") as req:
        req.side_effect = [_response(card), _response(task), _response(task)]
        assert client.connect()
        session = client.session
        client.send_message("hi")
        client.get_task("t1")
        assert client.session is session
        assert req.call_count == 3


def test_bare_requests_request_is_not_used():
    client = A2AClient(agent_url="http://peer.example")
    with (
        mock.patch("requests.request") as bare,
        mock.patch("requests.Session.request", return_value=_response({})),
    ):
        client._http("GET", CARD_URL)
    bare.assert_not_called()


def test_disconnect_closes_session():
    client = A2AClient(agent_url="http://peer.example")
    session = client.session
    with mock.patch.object(session, "close") as close:
        client.disconnect()
    close.assert_called_once()
    assert client._session is None


def test_context_manager_closes_session():
    with A2AClient(agent_url="http://peer.example") as client:
        session = client.session
        with mock.patch.object(session, "close") as close:
            pass
    close.assert_not_called()
    assert client._session is None


def test_registry_reuses_client_per_url():
    reg = A2ARegistry(config_path="/tmp/unused-a2a.json")
    a = reg.client_for("http://peer.example/")
    b = reg.client_for("http://peer.example")
    assert a is b
    with mock.patch.object(a, "disconnect") as disc:
        reg.close()
    disc.assert_called_once()
    assert reg.client_for("http://peer.example") is not a


def test_select_interface_prefers_highest_version_even_when_listed_later():
    card = _card(
        [
            {
                "url": "http://peer.example/v03",
                "protocolBinding": "JSONRPC",
                "protocolVersion": "0.3.0",
            },
            {
                "url": "http://peer.example/v03rest",
                "protocolBinding": "HTTP+JSON",
                "protocolVersion": "0.3",
            },
            {
                "url": "http://peer.example/a2a/jsonrpc",
                "protocolBinding": "JSONRPC",
                "protocolVersion": "1.0",
            },
        ]
    )
    chosen = A2AClient._select_interface(card)
    assert chosen["url"] == "http://peer.example/a2a/jsonrpc"


def test_select_interface_binding_preference_within_same_version():
    card = _card(
        [
            {"url": "u1", "protocolBinding": "JSONRPC", "protocolVersion": "1.0"},
            {"url": "u2", "protocolBinding": "HTTP+JSON", "protocolVersion": "1.0"},
        ]
    )
    assert A2AClient._select_interface(card)["url"] == "u2"


def test_select_interface_unknown_version_ranks_last_and_falls_back_to_first():
    card = _card(
        [
            {"url": "u1", "protocolBinding": "GRPC", "protocolVersion": "99.0"},
            {"url": "u2", "protocolBinding": "GRPC", "protocolVersion": "0.3"},
        ]
    )
    assert A2AClient._select_interface(card)["url"] == "u2"
    assert A2AClient._select_interface(_card([]) ) == {}
