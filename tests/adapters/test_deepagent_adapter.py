#!/usr/bin/env python3
"""
Test script for DeepAgent framework adapter.

This script tests:
1. Compilation from SuperSpec playbook to DeepAgent code
2. Component creation via Framework Registry
3. Universal GEPA optimization
"""

from pathlib import Path
import pytest
from rich.console import Console

console = Console()


def test_deepagent_compilation():
    """Test DeepAgent compilation from playbook."""
    console.print("\n[bold cyan]Testing DeepAgent Compilation[/]")
    console.print("=" * 80)

    # Create minimal test playbook
    playbook = {
        "metadata": {
            "name": "test_deepagent",
            "version": "1.0.0",
            "description": "Test DeepAgent for compilation",
            "framework": "deepagents",
        },
        "spec": {
            "persona": {
                "role": "You are a helpful research assistant powered by DeepAgent.",
                "goal": "Help users with research tasks using planning and subagents.",
                "backstory": "You have access to planning tools and can delegate to specialized subagents.",
            },
            "language_model": {
                "model": "anthropic:claude-sonnet-4-20250514",
                "provider": "anthropic",
            },
            "input_fields": [
                {"name": "query", "type": "string", "description": "User query"}
            ],
            "output_fields": [
                {"name": "response", "type": "string", "description": "Agent response"}
            ],
            "reasoning": {
                "method": "deep-agent",
                "steps": [
                    "Understand the user's research request",
                    "Break down complex tasks using planning tools",
                    "Delegate to specialized subagents if needed",
                    "Synthesize results and provide comprehensive answer",
                ],
            },
            "feature_specifications": {
                "scenarios": [
                    {
                        "name": "Basic Research Query",
                        "input": {"query": "What is LangGraph?"},
                        "expected_output": {
                            "expected_keywords": ["langgraph", "graph", "langchain"]
                        },
                    }
                ]
            },
        },
    }

    # Compile
    from superoptix.adapters.framework_registry import FrameworkRegistry

    output_path = Path("test_deepagent_output.py")

    try:
        console.print("\n📦 [bold]Compiling playbook to DeepAgent code...[/]")

        result_path = FrameworkRegistry.compile_agent(
            framework="deepagents", playbook=playbook, output_path=str(output_path)
        )

        console.print(f"   ✅ Compiled to: {result_path}")

        # Read generated code
        generated_code = output_path.read_text()

        # Show sample of generated code
        console.print("\n📄 [bold]Generated code sample (first 50 lines):[/]")
        lines = generated_code.split("\n")[:50]
        for i, line in enumerate(lines, 1):
            console.print(f"   {i:3d} │ {line}")

        # Verify key components
        checks = [
            ("BaseComponent import", "from superoptix.core.base_component import"),
            ("DeepAgent import", "from superoptix.vendor.deepagents.graph import create_deep_agent"),
            ("Component class", "class TestDeepagentOutputComponent(BaseComponent)"),
            ("forward method", "def forward("),
            ("update method", "def update("),
            ("system_prompt variable", 'variable_type="system_prompt"'),
            ("framework identifier", 'framework="deepagents"'),
        ]

        console.print("\n🔍 [bold]Verifying generated code:[/]")
        for check_name, check_string in checks:
            if check_string in generated_code:
                console.print(f"   ✅ {check_name}")
            else:
                console.print(f"   ❌ {check_name} - NOT FOUND")
                raise AssertionError(f"{check_name} not found in generated code")

        console.print("\n[green]✅ All compilation checks passed![/]")

    finally:
        # Cleanup
        if output_path.exists():
            console.print(f"\n🧹 Cleaning up: {output_path}")
            output_path.unlink()


def test_deepagent_component_creation():
    """Test DeepAgent component creation."""
    console.print("\n\n[bold cyan]Testing DeepAgent Component Creation[/]")
    console.print("=" * 80)

    # Check if deepagents is installed
    try:
        import deepagents

        console.print("   ✅ DeepAgent library is installed")
    except ImportError:
        console.print(
            "\n[yellow]⚠️  DeepAgent library not installed. Skipping component creation test.[/]"
        )
        pytest.skip("DeepAgent library not installed")

    # Create test playbook
    playbook = {
        "metadata": {
            "name": "qa_agent",
            "version": "1.0.0",
            "description": "Simple Q&A agent using DeepAgent",
            "framework": "deepagents",
        },
        "spec": {
            "persona": {
                "role": "You are a helpful Q&A assistant.",
                "goal": "Answer user questions accurately and concisely.",
            },
            "language_model": {"model": "anthropic:claude-sonnet-4-20250514"},
            "feature_specifications": {
                "scenarios": [
                    {
                        "name": "Simple Q&A",
                        "input": {"query": "What is 2+2?"},
                        "expected_output": {"expected_keywords": ["4", "four"]},
                    }
                ]
            },
        },
    }

    console.print("\n📦 [bold]Creating DeepAgent component...[/]")

    from superoptix.adapters.framework_registry import FrameworkRegistry

    component = FrameworkRegistry.create_component(
        framework="deepagents", playbook=playbook
    )

    console.print(f"   ✅ Component created: {component.name}")

    # Verify component properties
    console.print("\n🔍 [bold]Component properties:[/]")
    console.print(f"   Name: {component.name}")
    console.print(f"   Framework: {component.framework}")
    console.print(f"   Optimizable: {component.optimizable}")
    console.print(f"   Variable type: {component.variable_type}")
    console.print(f"   Input fields: {component.input_fields}")
    console.print(f"   Output fields: {component.output_fields}")
    console.print(f"\n   System prompt (first 200 chars):")
    console.print(f"   {component.variable[:200]}...")

    # Verify it's optimizable
    if not component.optimizable:
        console.print("\n[red]❌ Component is not optimizable![/]")
        raise AssertionError("Component is not optimizable")

    if component.variable_type != "system_prompt":
        console.print(
            f"\n[red]❌ Wrong variable type: {component.variable_type} (expected 'system_prompt')[/]\n"
        )
        raise AssertionError(f"Wrong variable type: {component.variable_type}")

    console.print("\n[green]✅ Component creation successful![/]")


def test_deepagent_forward_pass():
    """Test DeepAgent forward pass (if DeepAgent is installed)."""
    console.print("\n\n[bold cyan]Testing DeepAgent Forward Pass[/]")
    console.print("=" * 80)

    try:
        import deepagents

        console.print("   ✅ DeepAgent library is installed")
    except ImportError:
        console.print(
            "\n[yellow]⚠️  DeepAgent library not installed. Skipping forward pass test.[/]"
        )
        pytest.skip("DeepAgent library not installed")

    # Create component
    playbook = {
        "metadata": {
            "name": "echo_agent",
            "version": "1.0.0",
            "description": "Echo agent for testing",
            "framework": "deepagents",
        },
        "spec": {
            "persona": {
                "role": "You are a simple echo assistant. Repeat what the user says."
            },
            "language_model": {"model": "anthropic:claude-sonnet-4-20250514"},
        },
    }

    from superoptix.adapters.framework_registry import FrameworkRegistry

    component = FrameworkRegistry.create_component(
        framework="deepagents", playbook=playbook
    )

    console.print("\n🚀 [bold]Running forward pass...[/]")
    console.print("   Input: 'Hello, DeepAgent!'")

    result = component.forward(messages="Hello, DeepAgent!")

    console.print(f"\n   ✅ Output: {result.get('response', 'N/A')}")
    console.print("\n[green]✅ Forward pass successful![/]")
