"""Tests for the routing-quality metric and GEPA optimisation over the IR.

The claim this measures: a gateway makes an agent reachable, but only the
quality of its Agent Card makes it *worth reaching*. These tests pin that the
metric actually detects the difference, and that optimisation moves it.
"""

from __future__ import annotations

import json

import pytest

from superoptix.protocols.a2a.routing import (
    LexicalRouter,
    LLMRouter,
    SkillRef,
    catalogue_from_cards,
    generate_cases,
    score_routing,
    skills_from_card,
)
from superoptix.protocols.a2a.routing.optimize import (
    make_evaluator,
    seed_candidate,
)
from superoptix.protocols.a2a.routing.queries import RoutingCase

# Four sibling skills in one domain. The two catalogues differ *only* in how
# each skill describes itself.
_VAGUE = [
    SkillRef("billing", "billing", "Handle billing query", "Handle a customer query"),
    SkillRef("refunds", "refunds", "Process refund", "Handle a customer request"),
    SkillRef("tech", "tech", "Technical support", "Help the customer with the product"),
    SkillRef("accounts", "accounts", "Account help", "Assist a customer"),
]

_SPECIFIC = [
    SkillRef("billing", "billing", "Handle billing query",
             "Resolve invoice disputes, duplicate charges, payment failures and "
             "subscription price questions"),
    SkillRef("refunds", "refunds", "Process refund",
             "Decide and process refund and money-back requests, including returns "
             "and partial refunds"),
    SkillRef("tech", "tech", "Technical support",
             "Debug product crashes, upload errors, broken integrations that stop "
             "syncing, and login failures"),
    SkillRef("accounts", "accounts", "Account help",
             "Change workspace seats, account settings, permissions and the email "
             "on a login"),
]

# Caller vocabulary. Nobody recites a skill's title when they ask for help.
_CASES = [
    RoutingCase("I was charged twice for the same invoice", "billing:billing", "s"),
    RoutingCase("my subscription price went up unexpectedly", "billing:billing", "s"),
    RoutingCase("I want my money back for last month", "refunds:refunds", "s"),
    RoutingCase("can I return this and get a refund", "refunds:refunds", "s"),
    RoutingCase("the app crashes when I upload a file", "tech:tech", "s"),
    RoutingCase("our integration stopped syncing and throws errors", "tech:tech", "s"),
    RoutingCase("please add three more seats to our workspace", "accounts:accounts", "s"),
    RoutingCase("I need to change the email on my login", "accounts:accounts", "s"),
]


class TestMetricDetectsDescriptionQuality:
    """The metric has to move on description quality, or it measures nothing."""

    def test_vague_descriptions_route_badly(self):
        report = score_routing(LexicalRouter(), _VAGUE, _CASES)
        assert report.invocation_rate < 0.3

    def test_specific_descriptions_route_well(self):
        report = score_routing(LexicalRouter(), _SPECIFIC, _CASES)
        assert report.invocation_rate > 0.9

    def test_the_gap_is_large(self):
        """Same skills, same queries — only the descriptions differ."""
        vague = score_routing(LexicalRouter(), _VAGUE, _CASES).invocation_rate
        specific = score_routing(LexicalRouter(), _SPECIFIC, _CASES).invocation_rate
        assert specific - vague > 0.6

    def test_discovery_and_invocation_are_separate_signals(self):
        """A skill can be surfaced and still lose. They fail differently."""
        report = score_routing(LexicalRouter(), _VAGUE, _CASES)
        assert report.discovery_rate >= report.invocation_rate

    def test_misroutes_name_what_won_instead(self):
        report = score_routing(LexicalRouter(), _VAGUE, _CASES)
        assert report.misroutes
        assert {"query", "expected", "got"} <= set(report.misroutes[0])

    def test_empty_case_set_scores_zero_rather_than_dividing_by_zero(self):
        report = score_routing(LexicalRouter(), _VAGUE, [])
        assert report.cases == 0
        assert report.invocation_rate == 0.0


class TestRouter:
    def test_ranks_every_candidate(self):
        choice = LexicalRouter().route("duplicate charge on my invoice", _SPECIFIC)
        assert len(choice.ranked) == len(_SPECIFIC)
        assert choice.skill.key == "billing:billing"

    def test_no_skills_means_no_choice(self):
        assert LexicalRouter().route("anything", []).skill is None

    def test_a_query_of_only_stopwords_matches_nothing(self):
        assert LexicalRouter().route("the and of", _SPECIFIC).skill is None

    def test_llm_router_reads_the_identifier_back(self):
        router = LLMRouter(lm=lambda prompt: "I would call [tech:tech] for this.")
        assert router.route("app crashed", _SPECIFIC).skill.key == "tech:tech"

    def test_llm_router_handles_an_unparseable_reply(self):
        router = LLMRouter(lm=lambda prompt: "not sure")
        assert router.route("app crashed", _SPECIFIC).skill is None


class TestCatalogue:
    def test_flattens_skills_out_of_a_card(self):
        card = {
            "name": "SupportBot",
            "skills": [
                {"id": "triage", "name": "Triage", "description": "d", "tags": ["t"]}
            ],
        }
        skills = skills_from_card(card)
        assert skills[0].key == "SupportBot:triage"

    def test_merges_several_cards(self):
        cards = [
            {"name": "A", "skills": [{"id": "x", "description": "d"}]},
            {"name": "B", "skills": [{"id": "y", "description": "d"}]},
        ]
        assert {s.key for s in catalogue_from_cards(cards)} == {"A:x", "B:y"}


class TestGeneratedCases:
    def test_hard_mode_withholds_the_skill_name(self):
        """A query that echoes the title lets a useless description win on it."""
        skills = [SkillRef("A", "x", "Refund Processing", "d", examples=("money back",))]
        hard = generate_cases(skills, per_skill=4, hard=True)
        assert hard
        assert not any("refund processing" in c.query.lower() for c in hard)

    def test_easy_mode_includes_it(self):
        skills = [SkillRef("A", "x", "Refund Processing", "d")]
        easy = generate_cases(skills, per_skill=2, hard=False)
        assert any("refund processing" in c.query.lower() for c in easy)

    def test_a_skill_with_nothing_distinguishing_yields_no_hard_cases(self):
        """Not a gap in the generator: nothing about the skill is routable."""
        skills = [SkillRef("A", "x", "Thing", "does things")]
        assert generate_cases(skills, per_skill=4, hard=True) == []


class TestOptimizationContract:
    def test_seed_is_the_current_descriptions(self):
        seed = seed_candidate(_VAGUE)
        assert seed["billing:billing"] == "Handle a customer query"

    def test_evaluator_scores_a_correct_route(self):
        evaluate = make_evaluator(_SPECIFIC)
        score, info = evaluate(seed_candidate(_SPECIFIC), _CASES[0])
        assert score == 1.0
        assert "Correct" in info["feedback"]

    def test_evaluator_explains_a_miss(self):
        """GEPA reflects on the feedback, so it has to say what went wrong."""
        evaluate = make_evaluator(_VAGUE)
        score, info = evaluate(seed_candidate(_VAGUE), _CASES[0])
        assert score == 0.0
        assert "does not cover" in info["feedback"] or "instead of" in info["feedback"]

    def test_evaluator_returns_side_info_as_a_dict(self):
        """optimize_anything normalises a 2-tuple as (score, side_info dict)."""
        evaluate = make_evaluator(_VAGUE)
        _, info = evaluate(seed_candidate(_VAGUE), _CASES[0])
        assert isinstance(info, dict)

    def test_candidate_substitution_does_not_mutate_the_catalogue(self):
        evaluate = make_evaluator(_VAGUE)
        evaluate({"billing:billing": "rewritten"}, _CASES[0])
        assert _VAGUE[0].description == "Handle a customer query"

    def test_only_descriptions_are_optimisable(self):
        """Identity and protocol fields must stay out of GEPA's reach."""
        from superoptix.protocols.a2a.adapt.base import AgentSpec

        assert AgentSpec(
            name="n", description="d", framework="f", entrypoint="m:a"
        ).optimizable == ("skills[].description", "skills[].examples")


class TestGepaIntegration:
    def test_optimization_improves_a_vague_catalogue(self):
        """End-to-end through GEPA with a scripted reflection model."""
        pytest.importorskip("gepa")
        from superoptix.protocols.a2a.routing.optimize import optimize_routing

        improved = {
            "billing:billing": "Resolve invoice disputes, duplicate charges, "
            "payment failures and subscription price questions",
            "refunds:refunds": "Decide and process refund and money-back requests, "
            "including returns and partial refunds",
            "tech:tech": "Debug product crashes, upload errors, broken integrations "
            "that stop syncing, and login failures",
            "accounts:accounts": "Change workspace seats, account settings, "
            "permissions and the email on a login",
        }

        def reflection_lm(prompt, **kwargs):
            for key, text in improved.items():
                if key in str(prompt):
                    return text
            return next(iter(improved.values()))

        result = optimize_routing(
            _VAGUE,
            _CASES,
            reflection_lm=reflection_lm,
            router=LexicalRouter(),
            max_metric_calls=60,
        )
        assert result.baseline_score < 0.3
        assert result.improvement > 0
        assert json.dumps(result.optimized_descriptions)
