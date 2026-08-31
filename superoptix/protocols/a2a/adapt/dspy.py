"""Introspect a DSPy Module or Signature into the adapt IR.

A DSPy Signature is unusually good source material for an Agent Card: it already
names its inputs and outputs, carries per-field descriptions, and its docstring
is the task instruction. That maps almost directly onto a skill.
"""

from __future__ import annotations

from typing import Any, Dict, List

from superoptix.protocols.a2a.adapt.base import (
    AdaptError,
    AgentSpec,
    Skill,
    first_sentence,
    register,
    slugify,
)

# DSPy adds these to a signature itself; they are not part of the agent's
# declared interface and should not appear in the card.
_SYNTHETIC_FIELDS = {"reasoning", "rationale"}

# Class names DSPy generates internally. They say nothing to a calling agent,
# so a readable label is derived from the entrypoint instead.
_GENERIC_SIGNATURE_NAMES = {"StringSignature", "Signature", "SignatureMeta"}


def _readable_label(signature: Any, *, predictor_name: str, fallback: str) -> str:
    """Best human-facing name for a predictor's signature."""
    name = getattr(signature, "__name__", "") or ""
    if name and name not in _GENERIC_SIGNATURE_NAMES:
        return name
    if predictor_name and predictor_name not in {"self", "predict"}:
        return predictor_name.replace("_", " ").strip().title()
    return fallback.replace("_", " ").strip().title()


def _field_desc(field: Any) -> str:
    extra = getattr(field, "json_schema_extra", None) or {}
    if isinstance(extra, dict):
        return str(extra.get("desc") or "").strip()
    return ""


def _describe_fields(fields: Dict[str, Any]) -> str:
    parts = []
    for name, field in fields.items():
        if name in _SYNTHETIC_FIELDS:
            continue
        desc = _field_desc(field)
        parts.append(f"{name} ({desc})" if desc else name)
    return ", ".join(parts)


def _is_signature(obj: Any) -> bool:
    return (
        isinstance(obj, type)
        and hasattr(obj, "input_fields")
        and hasattr(obj, "output_fields")
    )


def _is_module(obj: Any) -> bool:
    return hasattr(obj, "predictors") and callable(getattr(obj, "predictors", None))


def _signature_skill(signature: Any, *, skill_id: str, label: str) -> Skill:
    inputs = dict(getattr(signature, "input_fields", {}) or {})
    outputs = dict(getattr(signature, "output_fields", {}) or {})
    instructions = str(getattr(signature, "instructions", "") or "").strip()

    described_in = _describe_fields(inputs)
    described_out = _describe_fields(outputs)

    description = instructions or f"Map {described_in} to {described_out}."
    if described_in and described_out and instructions:
        description = f"{instructions} Takes {described_in}; returns {described_out}."

    examples = []
    for name, field in inputs.items():
        if name in _SYNTHETIC_FIELDS:
            continue
        desc = _field_desc(field)
        if desc:
            examples.append(f"{name}: {desc}")
    return Skill(
        id=skill_id,
        name=label,
        description=first_sentence(description),
        tags=["dspy", "signature", *[n for n in inputs if n not in _SYNTHETIC_FIELDS]],
        examples=examples[:3],
        output_modes=["text/plain", "application/json"],
    )


class DSPyIntrospector:
    """Reads DSPy Modules and Signatures."""

    framework = "dspy"

    def matches(self, obj: Any) -> bool:
        return _is_signature(obj) or _is_module(obj)

    def introspect(self, obj: Any, *, entrypoint: str) -> AgentSpec:
        default_name = entrypoint.split(":")[-1].split(".")[-1]

        if _is_signature(obj):
            label = getattr(obj, "__name__", default_name)
            skill = _signature_skill(
                obj, skill_id=slugify(label, "signature"), label=label
            )
            return AgentSpec(
                name=label,
                description=skill.description,
                framework=self.framework,
                entrypoint=entrypoint,
                skills=[skill],
                metadata={"dspyKind": "signature"},
            )

        if not _is_module(obj):
            raise AdaptError(
                f"{entrypoint} resolved to {type(obj).__name__}, which is not a "
                "DSPy Module or Signature."
            )

        skills: List[Skill] = []
        try:
            named = list(obj.named_predictors())
        except Exception as exc:  # noqa: BLE001 - surface as an adapt error
            raise AdaptError(
                f"Could not read predictors from {entrypoint}: {exc}"
            ) from exc

        multiple = len(named) > 1
        for name, predictor in named:
            signature = getattr(predictor, "signature", None)
            if signature is None:
                continue
            label = _readable_label(
                signature, predictor_name=name, fallback=default_name
            )
            # With one predictor the module name is the better skill id; with
            # several, the predictor name is what distinguishes them.
            skill_id = slugify(name if multiple else default_name, "skill")
            skills.append(_signature_skill(signature, skill_id=skill_id, label=label))

        if not skills:
            raise AdaptError(
                f"{entrypoint} is a DSPy module with no readable predictor "
                "signatures to describe."
            )

        module_kind = type(obj).__name__
        return AgentSpec(
            name=default_name,
            description=(
                f"DSPy {module_kind} exposing {len(skills)} signature(s): "
                + ", ".join(s.name for s in skills)
            ),
            framework=self.framework,
            entrypoint=entrypoint,
            skills=skills,
            metadata={"dspyKind": "module", "dspyModule": module_kind},
        )


register(DSPyIntrospector())
