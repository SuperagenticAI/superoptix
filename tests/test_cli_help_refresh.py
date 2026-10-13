"""The CLI help leads with the 2.0 pillars and drops removed commands."""

import sys

import pytest

from superoptix.cli import main as cli_main


def _help(monkeypatch, capsys, *argv):
    monkeypatch.setattr(sys, "argv", ["super", *argv, "--help"])
    with pytest.raises(SystemExit):
        cli_main.main()
    return capsys.readouterr().out


def test_top_level_help_uses_locked_messaging(monkeypatch, capsys):
    out = _help(monkeypatch, capsys)
    assert "Optimization and Quality layer for AI agents" in out
    assert "Optimize agents. Connect over A2A. Ship with quality." in out
    assert "revolutionary" not in out
    assert out.index("init") < out.index("    agent") < out.index("    a2a")


def test_agent_help_lists_pillars_and_no_tier_status(monkeypatch, capsys):
    out = _help(monkeypatch, capsys, "agent")
    for cmd in ("optimize", "serve", "evaluate", "test"):
        assert f"super agent {cmd}" in out
    assert "tier-status" not in out
