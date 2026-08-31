"""A2A 1.0 error bindings and ProtoJSON error payloads.

The A2A specification binds each error to a JSON-RPC code, an HTTP status and a
gRPC status, and requires A2A-specific errors to carry a ``google.rpc.ErrorInfo``
entry (spec section 9.5). ErrorInfo travels in ``error.data`` on the JSON-RPC
binding and in ``error.details`` on HTTP+JSON, both using the ProtoJSON
``@type`` convention.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

ERROR_DOMAIN = "a2a-protocol.org"
ERRORINFO_TYPE = "type.googleapis.com/google.rpc.ErrorInfo"


@dataclass(frozen=True)
class A2AError:
    """One row of the A2A error binding table."""

    name: str
    jsonrpc_code: int
    http_status: int
    # Standard JSON-RPC errors carry no ErrorInfo reason.
    reason: str | None = None

    def error_info(self, metadata: Dict[str, str] | None = None) -> Dict[str, Any]:
        """Build the google.rpc.ErrorInfo entry for this error."""
        info: Dict[str, Any] = {
            "@type": ERRORINFO_TYPE,
            "domain": ERROR_DOMAIN,
            "reason": self.reason,
        }
        if metadata:
            info["metadata"] = {str(k): str(v) for k, v in metadata.items()}
        return info

    def details(self, metadata: Dict[str, str] | None = None) -> List[Dict[str, Any]]:
        """ProtoJSON detail array. Empty for standard JSON-RPC errors."""
        return [self.error_info(metadata)] if self.reason else []


# A2A-specific errors
TASK_NOT_FOUND = A2AError("TaskNotFoundError", -32001, 404, "TASK_NOT_FOUND")
TASK_NOT_CANCELABLE = A2AError(
    "TaskNotCancelableError", -32002, 409, "TASK_NOT_CANCELABLE"
)
PUSH_NOTIFICATION_NOT_SUPPORTED = A2AError(
    "PushNotificationNotSupportedError", -32003, 400, "PUSH_NOTIFICATION_NOT_SUPPORTED"
)
UNSUPPORTED_OPERATION = A2AError(
    "UnsupportedOperationError", -32004, 400, "UNSUPPORTED_OPERATION"
)
CONTENT_TYPE_NOT_SUPPORTED = A2AError(
    "ContentTypeNotSupportedError", -32005, 415, "CONTENT_TYPE_NOT_SUPPORTED"
)
INVALID_AGENT_RESPONSE = A2AError(
    "InvalidAgentResponseError", -32006, 502, "INVALID_AGENT_RESPONSE"
)
EXTENDED_AGENT_CARD_NOT_CONFIGURED = A2AError(
    "ExtendedAgentCardNotConfiguredError",
    -32007,
    400,
    "EXTENDED_AGENT_CARD_NOT_CONFIGURED",
)
EXTENSION_SUPPORT_REQUIRED = A2AError(
    "ExtensionSupportRequiredError", -32008, 400, "EXTENSION_SUPPORT_REQUIRED"
)
VERSION_NOT_SUPPORTED = A2AError(
    "VersionNotSupportedError", -32009, 400, "VERSION_NOT_SUPPORTED"
)

# Standard JSON-RPC errors: no ErrorInfo reason.
INVALID_REQUEST = A2AError("InvalidRequestError", -32600, 400)
METHOD_NOT_FOUND = A2AError("MethodNotFoundError", -32601, 404)
INVALID_PARAMS = A2AError("InvalidParamsError", -32602, 400)
INTERNAL = A2AError("InternalError", -32603, 500)
PARSE = A2AError("ParseError", -32700, 400)

ALL_ERRORS: Dict[str, A2AError] = {
    e.name: e
    for e in (
        TASK_NOT_FOUND,
        TASK_NOT_CANCELABLE,
        PUSH_NOTIFICATION_NOT_SUPPORTED,
        UNSUPPORTED_OPERATION,
        CONTENT_TYPE_NOT_SUPPORTED,
        INVALID_AGENT_RESPONSE,
        EXTENDED_AGENT_CARD_NOT_CONFIGURED,
        EXTENSION_SUPPORT_REQUIRED,
        VERSION_NOT_SUPPORTED,
        INVALID_REQUEST,
        METHOD_NOT_FOUND,
        INVALID_PARAMS,
        INTERNAL,
        PARSE,
    )
}


def jsonrpc_error_body(
    request_id: Any,
    error: A2AError,
    message: str,
    *,
    metadata: Dict[str, str] | None = None,
) -> Dict[str, Any]:
    """Build a JSON-RPC error envelope.

    Note this is returned with HTTP 200: in JSON-RPC the transport succeeded and
    the failure is carried inside the envelope. Returning a 4xx alongside it
    makes conformant clients treat the response as a transport failure and never
    read the error code.
    """
    body: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": error.jsonrpc_code, "message": message},
    }
    details = error.details(metadata)
    if details:
        body["error"]["data"] = details
    return body


def http_error_body(
    error: A2AError,
    message: str,
    *,
    metadata: Dict[str, str] | None = None,
) -> Dict[str, Any]:
    """Build an AIP-193 error body for the HTTP+JSON binding."""
    body: Dict[str, Any] = {
        "error": {
            "code": error.http_status,
            "message": message,
            "status": error.reason or error.name,
        }
    }
    details = error.details(metadata)
    if details:
        body["error"]["details"] = details
    return body
