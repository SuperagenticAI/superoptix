"""Optimise how an agent describes itself, using GEPA.

The optimisation target is the Agent Card's routing surface — skill
descriptions and examples — because that is what a calling agent reads when it
decides whether and how to invoke you. A gateway can route traffic to your
agent; it cannot make your agent worth routing to.

GEPA is a good fit for the same reason it works for `gskill`: the artifact is
text, the outcome is scored, and the reflection model can see *why* a routing
decision went wrong (which sibling stole the query) rather than only that it did.

Two rules keep the result honest:

- Identity and protocol fields are never optimisable. Only ``skills[].description``
  and ``skills[].examples`` are, matching what the adapt IR declares.
- The eval set must come from outside the card. Queries derived from the
  description under optimisation would make the score circular.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Sequence

from superoptix.protocols.a2a.routing.metrics import score_routing
from superoptix.protocols.a2a.routing.queries import RoutingCase
from superoptix.protocols.a2a.routing.router import LexicalRouter, Router, SkillRef


@dataclass
class OptimizationResult:
    """Before/after for a routing optimisation run."""

    baseline_score: float
    optimized_score: float
    baseline_descriptions: Dict[str, str]
    optimized_descriptions: Dict[str, str]
    validation_score: float | None = None
    validation_router: str | None = None
    heldout_baseline_score: float | None = None
    heldout_optimized_score: float | None = None
    heldout_size: int = 0
    train_size: int = 0
    split_digest: str | None = None
    holdout_fallback_reason: str | None = None

    @property
    def improvement(self) -> float:
        """Reported gain, measured on the cases GEPA optimised against."""
        return self.optimized_score - self.baseline_score

    @property
    def heldout_improvement(self) -> float | None:
        """Gain on held-out cases GEPA never saw. None without a split."""
        if self.heldout_baseline_score is None or self.heldout_optimized_score is None:
            return None
        return self.heldout_optimized_score - self.heldout_baseline_score

    def summary(self) -> str:
        line = (
            f"invocation (train) {self.baseline_score:.1%} → "
            f"{self.optimized_score:.1%} ({self.improvement:+.1%})"
        )
        if self.heldout_improvement is not None:
            line += (
                f" | held-out {self.heldout_baseline_score:.1%} → "
                f"{self.heldout_optimized_score:.1%} "
                f"({self.heldout_improvement:+.1%}, n={self.heldout_size})"
            )
        elif self.holdout_fallback_reason:
            line += f" | no held-out split: {self.holdout_fallback_reason}"
        if self.validation_score is not None:
            line += f" | {self.validation_router}: {self.validation_score:.1%}"
        return line


def _apply(skills: Sequence[SkillRef], candidate: Dict[str, str]) -> List[SkillRef]:
    """Rebuild the catalogue with candidate descriptions substituted in."""
    from dataclasses import replace

    return [
        replace(skill, description=candidate.get(skill.key, skill.description))
        for skill in skills
    ]


def seed_candidate(skills: Sequence[SkillRef]) -> Dict[str, str]:
    """The current descriptions — GEPA's starting point."""
    return {skill.key: skill.description for skill in skills}


def make_evaluator(
    skills: Sequence[SkillRef],
    router: Router | None = None,
) -> Callable[..., tuple[float, Dict[str, str]]]:
    """Score one candidate against one routing case, with text feedback.

    GEPA improves faster when it can read *why* a case failed, so the feedback
    names the sibling that won instead. The parameter is called ``example``
    because that is the keyword optimize_anything passes it under.
    """
    router = router or LexicalRouter()

    def evaluate(
        candidate: Dict[str, str], example: RoutingCase
    ) -> tuple[float, Dict[str, str]]:
        case = example
        catalogue = _apply(skills, candidate)
        choice = router.route(case.query, catalogue)
        chosen = choice.skill.key if choice.skill else None

        if chosen == case.expected:
            return 1.0, {
                "feedback": f"Correct: {case.query!r} routed to {case.expected}."
            }
        if chosen is None:
            return 0.0, {
                "feedback": (
                    f"Missed: {case.query!r} matched no skill. The description "
                    f"for {case.expected} does not cover the vocabulary this "
                    "request uses."
                )
            }
        return 0.0, {
            "feedback": (
                f"Misrouted: {case.query!r} went to {chosen} instead of "
                f"{case.expected}. Those two descriptions do not distinguish "
                "themselves from each other for this kind of request."
            )
        }

    return evaluate


def optimize_routing(
    skills: Sequence[SkillRef],
    cases: Sequence[RoutingCase],
    *,
    reflection_lm: Any,
    router: Router | None = None,
    validation_router: Router | None = None,
    max_metric_calls: int = 60,
    objective: str | None = None,
    valset_fraction: float = 0.2,
    seed: int = 0,
) -> OptimizationResult:
    """Run GEPA over the card's routing surface.

    Args:
        reflection_lm: the model GEPA reflects with.
        router: the router optimised against.
        validation_router: a *different* router used to re-score the winner.
            Optimising and scoring with one router measures that router's
            reading habits, not interoperability; a gain that survives the swap
            is a real one. It scores the held-out cases when a split exists.
        valset_fraction: share of cases held out from GEPA (seeded by
            ``seed``). Seed and optimised descriptions are scored on them so
            the held-out gain is not inflated by selection on the same cases
            (arXiv:2610.09239). Small case sets fall back to no split.
    """
    from gepa.optimize_anything import (
        EngineConfig,
        GEPAConfig,
        ReflectionConfig,
        optimize_anything,
    )

    from superoptix.optimizers.holdout import split_holdout

    router = router or LexicalRouter()
    seed_descriptions = seed_candidate(skills)
    split = split_holdout(list(cases), fraction=valset_fraction, seed=seed)
    dataset = list(split.train)
    heldout = list(split.heldout)

    baseline = score_routing(
        router, _apply(skills, seed_descriptions), dataset
    ).invocation_rate
    evaluator = make_evaluator(skills, router)

    result = optimize_anything(
        seed_descriptions,
        evaluator=evaluator,
        dataset=dataset,
        valset=dataset,  # held-out cases are never shown to GEPA
        objective=objective
        or (
            "Rewrite each agent skill description so that a calling agent "
            "routes real user requests to the correct skill. Descriptions must "
            "stay truthful about what the skill does, name the concrete "
            "vocabulary users bring, and distinguish each skill from its "
            "siblings."
        ),
        background=(
            "These are A2A Agent Card skill descriptions. Other agents read "
            "them to decide which skill to invoke. Do not invent capabilities "
            "the skill does not have."
        ),
        config=GEPAConfig(
            engine=EngineConfig(
                max_metric_calls=max_metric_calls,
                display_progress_bar=False,
            ),
            reflection=ReflectionConfig(reflection_lm=reflection_lm),
        ),
    )

    best = _best_candidate(result, seed_descriptions)
    optimized = score_routing(router, _apply(skills, best), dataset).invocation_rate

    heldout_baseline = heldout_optimized = None
    if heldout:
        heldout_baseline = score_routing(
            router, _apply(skills, seed_descriptions), heldout
        ).invocation_rate
        heldout_optimized = score_routing(
            router, _apply(skills, best), heldout
        ).invocation_rate

    validation_score = None
    validation_name = None
    if validation_router is not None:
        validation_score = score_routing(
            validation_router, _apply(skills, best), heldout or dataset
        ).invocation_rate
        validation_name = validation_router.name

    return OptimizationResult(
        baseline_score=baseline,
        optimized_score=optimized,
        baseline_descriptions=dict(seed_descriptions),
        optimized_descriptions=dict(best),
        validation_score=validation_score,
        validation_router=validation_name,
        heldout_baseline_score=heldout_baseline,
        heldout_optimized_score=heldout_optimized,
        heldout_size=len(heldout),
        train_size=len(dataset),
        split_digest=split.digest,
        holdout_fallback_reason=split.fallback_reason,
    )


def _best_candidate(result: Any, fallback: Dict[str, str]) -> Dict[str, str]:
    """Pull the winning candidate out of a GEPA result."""
    for attr in ("best_candidate", "best", "candidate"):
        value = getattr(result, attr, None)
        if isinstance(value, dict) and value:
            return {str(k): str(v) for k, v in value.items()}
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return {str(k): str(v) for k, v in parsed.items()}
            except (ValueError, TypeError):
                continue
    return dict(fallback)
