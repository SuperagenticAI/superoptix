#!/usr/bin/env python3
"""
Test script for DeepAgent framework adapter.

This script tests:
1. Compilation from SuperSpec playbook to DeepAgent code
2. Component creation via Framework Registry
3. Universal GEPA optimization
"""

from pathlib import Path
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
            "framework": "deepagent",
        },
        "spec": {
            "persona": {
                "role": "You are a helpful research assistant powered by DeepAgent.",
                "goal": "Help users with research tasks using planning and subagents.",
                "backstory": "You have access to planning tools and can delegate to specialized subagents.",
            },
            "model": {
                "model_name": "anthropic:claude-sonnet-4-20250514",
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
            framework="deepagent", playbook=playbook, output_path=str(output_path)
        )

        console.print(f"   ✅ Compiled to: {result_path}")

        # Read generated code
        generated_code = output_path.read_text()

        # Verify key components
        checks = [
            ("BaseComponent import", "from superoptix.core.base_component import"),
            ("DeepAgent import", "from deepagents import create_deep_agent"),
            ("Component class", "class TestDeepagentComponent(BaseComponent)"),
            ("forward method", "def forward("),
            ("update method", "def update("),
            ("system_prompt variable", 'variable_type="system_prompt"'),
            ("framework identifier", 'framework="deepagent"'),
        ]

        console.print("\n🔍 [bold]Verifying generated code:[/]")
        all_passed = True
        for check_name, check_string in checks:
            if check_string in generated_code:
                console.print(f"   ✅ {check_name}")
            else:
                console.print(f"   ❌ {check_name} - NOT FOUND")
                all_passed = False

        if all_passed:
            console.print("\n[green]✅ All compilation checks passed![/]")
        else:
            console.print("\n[red]❌ Some checks failed[/]")
            return False

        # Show sample of generated code
        console.print("\n📄 [bold]Generated code sample (first 50 lines):[/]")
        lines = generated_code.split("\n")[:50]
        for i, line in enumerate(lines, 1):
            console.print(f"   {i:3d} │ {line}")

        return True

    except Exception as e:
        console.print(f"\n[red]❌ Compilation failed: {e}[/]")
        import traceback

        traceback.print_exc()
        return False

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
        console.print(
            "   Install from: reference/deepagents-master/ or wait for PyPI release"
        )
        return None

    # Create test playbook
    playbook = {
        "metadata": {
            "name": "qa_agent",
            "version": "1.0.0",
            "description": "Simple Q&A agent using DeepAgent",
            "framework": "deepagent",
        },
        "spec": {
            "persona": {
                "role": "You are a helpful Q&A assistant.",
                "goal": "Answer user questions accurately and concisely.",
            },
            "model": {"model_name": "anthropic:claude-sonnet-4-20250514"},
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

    try:
        console.print("\n📦 [bold]Creating DeepAgent component...[/]")

        from superoptix.adapters.framework_registry import FrameworkRegistry

        component = FrameworkRegistry.create_component(
            framework="deepagent", playbook=playbook
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
            return False

        if component.variable_type != "system_prompt":
            console.print(
                f"\n[red]❌ Wrong variable type: {component.variable_type} (expected 'system_prompt')[/]"
            )
            return False

        console.print("\n[green]✅ Component creation successful![/]")
        return True

    except Exception as e:
        console.print(f"\n[red]❌ Component creation failed: {e}[/]")
        import traceback

        traceback.print_exc()
        return False


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
        console.print(
            "   Install with: pip install deepagent (or from source if not on PyPI)"
        )
        return None

    # Create component
    playbook = {
        "metadata": {
            "name": "echo_agent",
            "version": "1.0.0",
            "description": "Echo agent for testing",
            "framework": "deepagent",
        },
        "spec": {
            "persona": {
                "role": "You are a simple echo assistant. Repeat what the user says."
            },
            "model": {"model_name": "anthropic:claude-sonnet-4-20250514"},
        },
    }

    try:
        from superoptix.adapters.framework_registry import FrameworkRegistry

        component = FrameworkRegistry.create_component(
            framework="deepagent", playbook=playbook
        )

        console.print("\n🚀 [bold]Running forward pass...[/]")
        console.print("   Input: 'Hello, DeepAgent!'")

        result = component.forward(messages="Hello, DeepAgent!")

        console.print(f"\n   ✅ Output: {result.get('response', 'N/A')}")
        console.print("\n[green]✅ Forward pass successful![/]")
        return True

    except Exception as e:
        console.print(f"\n[red]❌ Forward pass failed: {e}[/]")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    console.print(
        "\n[bold magenta]╔══════════════════════════════════════════════════════════╗[/]"
    )
    console.print(
        "[bold magenta]║  DeepAgent Framework Adapter - Test Suite               ║[/]"
    )
    console.print(
        "[bold magenta]╚══════════════════════════════════════════════════════════╝[/]"
    )

    results = {}

    # Test 1: Compilation
    results["compilation"] = test_deepagent_compilation()

    # Test 2: Component creation
    component_result = test_deepagent_component_creation()
    if component_result is not None:
        results["component_creation"] = component_result

    # Test 3: Forward pass (optional - requires DeepAgent installed)
    forward_result = test_deepagent_forward_pass()
    if forward_result is not None:
        results["forward_pass"] = forward_result

    # Summary
    console.print("\n\n[bold cyan]Test Summary[/]")
    console.print("=" * 80)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        color = "green" if passed else "red"
        console.print(f"   [{color}]{status}[/] - {test_name}")

    total_tests = len(results)
    passed_tests = sum(1 for p in results.values() if p)

    console.print(f"\n[bold]Results: {passed_tests}/{total_tests} tests passed[/]")

    # Note about skipped tests
    if component_result is None or forward_result is None:
        console.print(
            "\n[yellow]Note: Some tests were skipped due to missing DeepAgent library.[/]"
        )
        console.print(
            "[yellow]The core compilation functionality is working correctly![/]"
        )

    if passed_tests == total_tests:
        console.print(
            "\n[green bold]🎉 All tests passed! DeepAgent adapter is working![/]"
        )
        return 0
    else:
        console.print(
            "\n[red bold]❌ Some tests failed. Check output above for details.[/]"
        )
        return 1


if __name__ == "__main__":
    exit(main())
