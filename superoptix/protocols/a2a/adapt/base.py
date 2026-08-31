"""The intermediate representation `super a2a adapt` compiles through.

SuperSpec is normally something a person writes. On the adapt path it is
*generated*: an introspector reads an agent someone already built and emits this
IR, and the emitters turn the IR into an A2A 1.0 Agent Card and a conformant
server. The user never writes a SuperSpec and may never see one.

That indirection is what makes eight frameworks tractable — each needs one
introspector in and shares every emitter out — and it gives GEPA a structured
target when it later optimises how the agent is described to callers.
"""

from __future__ import annotations

import importlib
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Protocol


class AdaptError(Exception):
    """Raised when an agent cannot be introspected into the IR."""


@dataclass
class Skill:
    """One callable capability, as a calling agent will read it."""

    id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    input_modes: List[str] = field(default_factory=lambda: ["text/plain"])
    output_modes: List[str] = field(default_factory=lambda: ["text/plain"])

    def to_card_skill(self) -> Dict[str, Any]:
        skill: Dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tags": list(self.tags),
            "inputModes": list(self.input_modes),
            "outputModes": list(self.output_modes),
        }
        if self.examples:
            skill["examples"] = list(self.examples)
        return skill


@dataclass
class AgentSpec:
    """The generated SuperSpec: everything the emitters need, framework-neutral.

    ``optimizable`` names the fields GEPA may rewrite. Skill descriptions and
    examples are the routing interface other agents read, so they are the
    surface worth optimising; identity and protocol fields are not.
    """

    name: str
    description: str
    framework: str
    entrypoint: str
    version: str = "1.0.0"
    skills: List[Skill] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    optimizable: tuple[str, ...] = ("skills[].description", "skills[].examples")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "apiVersion": "agent/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "framework": self.framework,
                "entrypoint": self.entrypoint,
                **self.metadata,
            },
            "spec": {
                "skills": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "description": s.description,
                        "tags": list(s.tags),
                        "examples": list(s.examples),
                        "inputModes": list(s.input_modes),
                        "outputModes": list(s.output_modes),
                    }
                    for s in self.skills
                ],
            },
            "optimizable": list(self.optimizable),
        }


def slugify(value: str, fallback: str = "skill") -> str:
    """Lowercase, hyphenated identifier safe for an Agent Card skill id."""
    slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    return slug or fallback


def first_sentence(text: str, limit: int = 240) -> str:
    """Trim free-form prose to a single readable sentence."""
    flat = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(flat) <= limit:
        return flat
    cut = flat[:limit]
    return cut[: cut.rfind(" ")] + "…" if " " in cut else cut


def load_entrypoint(entrypoint: str) -> Any:
    """Import ``module:attribute`` and return the object.

    Calls zero-argument factories so both ``mycrew:crew`` (an instance) and
    ``mycrew:build_crew`` (a factory) work without the user knowing which the
    introspector wanted.
    """
    if ":" not in entrypoint:
        raise AdaptError(
            f"Entrypoint must be 'module:attribute', got {entrypoint!r}. "
            "Example: --entrypoint mycrew:crew"
        )
    module_name, _, attr = entrypoint.partition(":")
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise AdaptError(
            f"Could not import module {module_name!r}: {exc}. "
            "Run from the project root, or set PYTHONPATH."
        ) from exc

    obj: Any = module
    for part in attr.split("."):
        if not hasattr(obj, part):
            raise AdaptError(f"{module_name!r} has no attribute {attr!r}")
        obj = getattr(obj, part)

    # Only a plain factory function is called. Agent objects are frequently
    # callable themselves (a DSPy module accepts **kwargs), and invoking one
    # here would execute the user's agent — needing an LM — just to read its
    # shape. Introspection must never run the agent.
    if _is_factory_function(obj) and _takes_no_required_args(obj):
        try:
            obj = obj()
        except TypeError:
            pass
    return obj


def _is_factory_function(obj: Any) -> bool:
    import types

    return isinstance(obj, (types.FunctionType, types.LambdaType)) and not isinstance(
        obj, type
    )


def _takes_no_required_args(fn: Callable[..., Any]) -> bool:
    import inspect

    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return False
    return all(
        p.default is not inspect.Parameter.empty
        or p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
        for p in sig.parameters.values()
    )


class Introspector(Protocol):
    """Reads a framework-native agent and emits the IR."""

    framework: str

    def matches(self, obj: Any) -> bool:
        """Whether this introspector recognises the loaded object."""

    def introspect(self, obj: Any, *, entrypoint: str) -> AgentSpec:
        """Build an AgentSpec from the agent."""


_INTROSPECTORS: Dict[str, Introspector] = {}


def register(introspector: Introspector) -> None:
    _INTROSPECTORS[introspector.framework] = introspector


def get(framework: str) -> Introspector:
    key = str(framework or "").strip().lower().replace("_", "-")
    if key not in _INTROSPECTORS:
        available = ", ".join(sorted(_INTROSPECTORS)) or "none"
        raise AdaptError(f"No introspector for {framework!r}. Available: {available}")
    return _INTROSPECTORS[key]


def available() -> List[str]:
    return sorted(_INTROSPECTORS)


def detect(obj: Any) -> Introspector | None:
    """Find an introspector that recognises this object."""
    for introspector in _INTROSPECTORS.values():
        try:
            if introspector.matches(obj):
                return introspector
        except Exception:  # noqa: BLE001 - a probe must never break detection
            continue
    return None
