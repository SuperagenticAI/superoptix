"""Tests for `super a2a adapt` — the brownfield path.

The premise is that a user points SuperOptiX at an agent they already wrote and
gets an A2A endpoint without changing their code. These tests use duck-typed
stand-ins for CrewAI and DSPy objects so the contract is pinned without
requiring either framework to be installed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from superoptix.protocols.a2a.adapt import (
    AdaptError,
    available,
    build_card,
    detect,
    emit,
    get,
    load_entrypoint,
)
from superoptix.protocols.a2a.adapt.crewai import CrewAIIntrospector
from superoptix.protocols.a2a.adapt.dspy import DSPyIntrospector
from superoptix.protocols.a2a.adapt.invoke import _as_text, invoke_agent


# --------------------------------------------------------------------------
# Duck-typed stand-ins
# --------------------------------------------------------------------------
class _Agent:
    """Shaped like crewai.Agent."""

    def __init__(self, role, goal="", backstory="", tools=None):
        self.role, self.goal, self.backstory = role, goal, backstory
        self.tools = tools or []


_Agent.__name__ = "Agent"


class _Task:
    """Shaped like crewai.Task."""

    def __init__(self, name="", description="", expected_output="", agent=None):
        self.name, self.description = name, description
        self.expected_output, self.agent = expected_output, agent


_Task.__name__ = "Task"


class _Crew:
    """Shaped like crewai.Crew."""

    def __init__(self, agents=None, tasks=None, name=""):
        self.agents, self.tasks, self.name = agents or [], tasks or [], name
        self.kicked_off_with = None

    def kickoff(self, inputs=None):
        self.kicked_off_with = inputs
        return SimpleNamespace(raw="crew result")


_Crew.__name__ = "Crew"


def _field(desc):
    return SimpleNamespace(json_schema_extra={"desc": desc})


class _Signature:
    instructions = "Classify a support ticket and draft a reply."
    input_fields = {"ticket": _field("the raw ticket text")}
    output_fields = {
        "category": _field("billing, technical or account"),
        "reply": _field("a drafted response"),
        "reasoning": _field("internal scratchpad"),
    }


class _DSPyProgram:
    """Shaped like a dspy Module. Callable, as real ones are."""

    def __init__(self):
        self.called_with = None

    def named_predictors(self):
        return [("predict", SimpleNamespace(signature=_Signature))]

    def predictors(self):
        return [p for _, p in self.named_predictors()]

    def __call__(self, **kwargs):
        self.called_with = kwargs
        return {"category": "billing", "reply": "on it", "reasoning": "hidden"}


# --------------------------------------------------------------------------
# Entrypoint loading
# --------------------------------------------------------------------------
class TestLoadEntrypoint:
    @pytest.fixture()
    def fake_module(self, monkeypatch):
        mod = ModuleType("adapt_fixture_mod")
        mod.crew = _Crew(agents=[_Agent("Analyst")])
        mod.program = _DSPyProgram()
        mod.build = lambda: _Crew(agents=[_Agent("Built")], name="factory-made")
        mod.needs_args = lambda x: x
        monkeypatch.setitem(sys.modules, "adapt_fixture_mod", mod)
        return mod

    def test_loads_an_instance(self, fake_module):
        assert load_entrypoint("adapt_fixture_mod:crew") is fake_module.crew

    def test_calls_a_zero_arg_factory(self, fake_module):
        loaded = load_entrypoint("adapt_fixture_mod:build")
        assert isinstance(loaded, _Crew)
        assert loaded.name == "factory-made"

    def test_never_invokes_a_callable_agent(self, fake_module):
        """Regression: introspection must not run the user's agent.

        A DSPy module is callable with **kwargs, so a naive "call it if it takes
        no required args" check executed the program — which needs a configured
        LM just to read the agent's shape.
        """
        loaded = load_entrypoint("adapt_fixture_mod:program")
        assert loaded is fake_module.program
        assert fake_module.program.called_with is None

    def test_leaves_functions_needing_arguments_alone(self, fake_module):
        assert callable(load_entrypoint("adapt_fixture_mod:needs_args"))

    def test_rejects_a_malformed_entrypoint(self):
        with pytest.raises(AdaptError, match="module:attribute"):
            load_entrypoint("no_colon_here")

    def test_reports_a_missing_attribute(self, fake_module):
        with pytest.raises(AdaptError, match="no attribute"):
            load_entrypoint("adapt_fixture_mod:nope")


# --------------------------------------------------------------------------
# Introspection
# --------------------------------------------------------------------------
class TestCrewAIIntrospection:
    def test_tasks_become_skills(self):
        crew = _Crew(
            agents=[_Agent("Researcher", goal="find sources")],
            tasks=[
                _Task(
                    name="Research topic",
                    description="Search the web for background on the topic",
                    expected_output="a sourced summary",
                    agent=_Agent("Researcher"),
                )
            ],
            name="research-crew",
        )
        spec = CrewAIIntrospector().introspect(crew, entrypoint="m:crew")
        assert spec.framework == "crewai"
        assert spec.name == "research-crew"
        skill = spec.skills[0]
        assert skill.id == "research-topic"
        assert "Search the web" in skill.description
        assert "a sourced summary" in skill.description
        assert "researcher" in skill.tags

    def test_falls_back_to_agents_when_there_are_no_tasks(self):
        crew = _Crew(agents=[_Agent("Analyst", goal="analyse the numbers")])
        spec = CrewAIIntrospector().introspect(crew, entrypoint="m:crew")
        assert [s.id for s in spec.skills] == ["analyst"]
        assert "analyse the numbers" in spec.skills[0].description

    def test_a_bare_agent_is_adaptable(self):
        spec = CrewAIIntrospector().introspect(
            _Agent("Support Bot", goal="answer questions"), entrypoint="m:agent"
        )
        assert spec.name == "Support Bot"
        assert len(spec.skills) == 1

    def test_an_empty_crew_is_an_error(self):
        with pytest.raises(AdaptError, match="no tasks or agents"):
            CrewAIIntrospector().introspect(_Crew(), entrypoint="m:crew")


class TestDSPyIntrospection:
    def test_signature_becomes_a_skill(self):
        spec = DSPyIntrospector().introspect(_DSPyProgram(), entrypoint="app:program")
        assert spec.framework == "dspy"
        skill = spec.skills[0]
        assert skill.description.startswith("Classify a support ticket")
        assert "ticket" in skill.description
        assert "category" in skill.description

    def test_dspy_internal_fields_are_not_advertised(self):
        """`reasoning` is DSPy's scratchpad, not part of the agent's interface."""
        spec = DSPyIntrospector().introspect(_DSPyProgram(), entrypoint="app:program")
        assert "reasoning" not in spec.skills[0].description
        assert "reasoning" not in spec.skills[0].tags

    def test_generic_signature_names_are_not_used_as_labels(self):
        class _Generic(_DSPyProgram):
            def named_predictors(self):
                sig = type("StringSignature", (_Signature,), {})
                return [("predict", SimpleNamespace(signature=sig))]

        spec = DSPyIntrospector().introspect(_Generic(), entrypoint="app:triage_bot")
        assert spec.skills[0].name == "Triage Bot"

    def test_a_module_without_signatures_is_an_error(self):
        class _Empty:
            def named_predictors(self):
                return []

            def predictors(self):
                return []

        with pytest.raises(AdaptError, match="no readable predictor"):
            DSPyIntrospector().introspect(_Empty(), entrypoint="m:x")


class TestDetection:
    def test_both_frameworks_are_registered(self):
        assert set(available()) >= {"crewai", "dspy"}

    def test_detects_without_an_explicit_framework(self):
        assert detect(_Crew(agents=[_Agent("A")])).framework == "crewai"
        assert detect(_DSPyProgram()).framework == "dspy"

    def test_unknown_framework_is_an_error(self):
        with pytest.raises(AdaptError, match="No introspector"):
            get("langchain")


# --------------------------------------------------------------------------
# Emitted artifacts
# --------------------------------------------------------------------------
class TestEmit:
    @pytest.fixture()
    def spec(self):
        crew = _Crew(
            agents=[_Agent("Researcher")],
            tasks=[_Task(name="Summarise", description="Summarise a document")],
            name="doc-crew",
        )
        return CrewAIIntrospector().introspect(crew, entrypoint="mycrew:crew")

    def test_card_advertises_both_spec_lines(self, spec):
        card = build_card(spec, public_url="https://agents.example.com")
        versions = {i["protocolVersion"] for i in card["supportedInterfaces"]}
        assert versions == {"1.0", "0.3"}
        assert card["protocolVersion"] == "1.0"

    def test_card_carries_the_discovered_skills(self, spec):
        card = build_card(spec, public_url="https://agents.example.com")
        assert [s["id"] for s in card["skills"]] == ["summarise"]

    def test_writes_card_server_and_ir(self, spec, tmp_path: Path):
        written = emit(spec, tmp_path, public_url="http://127.0.0.1:8000")
        names = {p.name for p in written}
        assert names == {"agent-card.json", "a2a_server.py", "agentspec.json"}

    def test_emitted_server_is_valid_python(self, spec, tmp_path: Path):
        import ast

        written = emit(spec, tmp_path, public_url="http://127.0.0.1:8000")
        server = next(p for p in written if p.name == "a2a_server.py")
        ast.parse(server.read_text())
        assert "mycrew:crew" in server.read_text()

    def test_ir_records_what_gepa_may_rewrite(self, spec, tmp_path: Path):
        """The IR is the optimisation target; identity fields are off limits."""
        written = emit(spec, tmp_path, public_url="http://127.0.0.1:8000")
        ir = json.loads(next(p for p in written if p.name == "agentspec.json").read_text())
        assert ir["optimizable"] == ["skills[].description", "skills[].examples"]
        assert ir["metadata"]["entrypoint"] == "mycrew:crew"


# --------------------------------------------------------------------------
# Invocation bridge
# --------------------------------------------------------------------------
class TestInvoke:
    @pytest.mark.asyncio
    async def test_crewai_is_called_through_kickoff(self):
        crew = _Crew()
        result = await invoke_agent(crew, "crewai", "hello")
        assert crew.kicked_off_with == {"query": "hello"}
        assert result["response"] == "crew result"

    @pytest.mark.asyncio
    async def test_dspy_is_called_with_its_own_input_field(self):
        program = _DSPyProgram()
        await invoke_agent(program, "dspy", "my ticket")
        assert program.called_with == {"ticket": "my ticket"}

    @pytest.mark.asyncio
    async def test_unknown_framework_is_rejected(self):
        with pytest.raises(ValueError, match="No invoker"):
            await invoke_agent(object(), "langchain", "hi")

    def test_multi_field_results_are_labelled(self):
        text = _as_text({"category": "billing", "reply": "on it"})
        assert "category: billing" in text
        assert "reply: on it" in text

    def test_single_field_results_are_returned_bare(self):
        assert _as_text({"answer": "42", "reasoning": "hidden"}) == "42"

    def test_internal_fields_are_not_returned(self):
        assert "hidden" not in _as_text({"answer": "42", "reasoning": "hidden"})
