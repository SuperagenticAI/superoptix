#!/usr/bin/env python3
"""
Test Universal GEPA with DeepAgent framework.

This tests that:
1. DeepAgent adapter integrates with Universal GEPA
2. Component can be created from playbook
3. System prompt is extracted as optimizable variable
"""

from rich.console import Console

console = Console()


def test_deepagent_gepa_integration():
    """Test DeepAgent integration with Universal GEPA."""
    console.print("\n[bold cyan]Testing DeepAgent + Universal GEPA Integration[/]")
    console.print("=" * 80)

    # Check if deepagents is installed
    try:
        import deepagents

        console.print("   ✅ DeepAgent library is installed")
        deepagent_available = True
    except ImportError:
        console.print("\n[yellow]⚠️  DeepAgent library not installed.[/]")
        console.print(
            "   We'll test the integration logic without running actual optimization."
        )
        deepagent_available = False

    # Create test playbook
    playbook = {
        "metadata": {
            "name": "research_agent",
            "version": "1.0.0",
            "description": "Research assistant using DeepAgent",
            "framework": "deepagent",
        },
        "spec": {
            "persona": {
                "role": "You are a helpful research assistant.",
                "goal": "Help users find accurate information.",
                "backstory": "You are powered by DeepAgent with planning capabilities.",
            },
            "model": {"model_name": "anthropic:claude-sonnet-4-20250514"},
            "input_fields": [
                {"name": "query", "type": "string", "description": "Research query"}
            ],
            "output_fields": [
                {"name": "response", "type": "string", "description": "Research answer"}
            ],
            "feature_specifications": {
                "scenarios": [
                    {
                        "name": "Basic Research",
                        "input": {"query": "What is LangGraph?"},
                        "expected_output": {
                            "expected_keywords": ["langgraph", "graph", "agent"]
                        },
                    },
                    {
                        "name": "Complex Research",
                        "input": {"query": "Explain multi-agent systems"},
                        "expected_output": {
                            "expected_keywords": [
                                "multi-agent",
                                "collaboration",
                                "systems",
                            ]
                        },
                    },
                ]
            },
        },
    }

    try:
        # Test 1: Verify DeepAgent adapter exists
        console.print("\n🔍 [bold]Test 1: Checking DeepAgent adapter...[/]")
        from superoptix.adapters.framework_registry import FrameworkRegistry

        if FrameworkRegistry.is_supported("deepagent"):
            console.print("   ✅ DeepAgent framework is registered")
        else:
            console.print("   ❌ DeepAgent framework not found")
            return False

        # Test 2: Get adapter info
        console.print("\n🔍 [bold]Test 2: Getting framework info...[/]")
        info = FrameworkRegistry.get_framework_info("deepagent")
        console.print(f"   Name: {info['name']}")
        console.print(f"   Requires async: {info['requires_async']}")
        console.print(f"   Implemented: {info['implemented']}")

        if not info["implemented"]:
            console.print("   ❌ DeepAgent adapter not implemented")
            return False

        console.print("   ✅ DeepAgent adapter is fully implemented")

        # Test 3: Extract optimizable variable
        console.print("\n🔍 [bold]Test 3: Extracting optimizable variable...[/]")
        adapter = FrameworkRegistry.get_adapter("deepagent")
        system_prompt = adapter.get_optimizable_variable(playbook)

        console.print(f"   System prompt: {system_prompt[:100]}...")

        if not system_prompt:
            console.print("   ❌ Failed to extract system prompt")
            return False

        console.print("   ✅ System prompt extracted successfully")

        # Test 4: Component creation (if DeepAgent is available)
        if deepagent_available:
            console.print("\n🔍 [bold]Test 4: Creating DeepAgent component...[/]")
            component = FrameworkRegistry.create_component(
                framework="deepagent", playbook=playbook
            )

            console.print(f"   Name: {component.name}")
            console.print(f"   Framework: {component.framework}")
            console.print(f"   Optimizable: {component.optimizable}")
            console.print(f"   Variable type: {component.variable_type}")

            if not component.optimizable:
                console.print("   ❌ Component is not optimizable")
                return False

            if component.framework != "deepagent":
                console.print(f"   ❌ Wrong framework: {component.framework}")
                return False

            console.print("   ✅ Component created successfully")

            # Test 5: Universal GEPA integration (mock test)
            console.print(
                "\n🔍 [bold]Test 5: Testing Universal GEPA compatibility...[/]"
            )

            # Verify component has required attributes for GEPA
            required_attrs = [
                "name",
                "framework",
                "variable",
                "variable_type",
                "forward",
                "update",
                "optimizable",
            ]

            for attr in required_attrs:
                if not hasattr(component, attr):
                    console.print(f"   ❌ Missing required attribute: {attr}")
                    return False
                console.print(f"   ✅ Has {attr}")

            console.print("\n   ✅ Component is compatible with Universal GEPA")

            # Test 6: Test update method
            console.print("\n🔍 [bold]Test 6: Testing update method...[/]")
            original_prompt = component.variable
            new_prompt = "Updated system prompt for testing"

            component.update(new_prompt)

            if component.variable != new_prompt:
                console.print("   ❌ Update method failed")
                return False

            console.print("   ✅ Update method works correctly")

            # Restore original
            component.update(original_prompt)

        else:
            console.print(
                "\n[yellow]⚠️  Skipping component creation and GEPA tests (DeepAgent not installed)[/]"
            )

        console.print("\n[green]✅ All tests passed![/]")
        console.print(
            "\n💡 DeepAgent framework is ready for Universal GEPA optimization!"
        )
        return True

    except Exception as e:
        console.print(f"\n[red]❌ Test failed: {e}[/]")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the test."""
    console.print(
        "\n[bold magenta]╔══════════════════════════════════════════════════════════╗[/]"
    )
    console.print(
        "[bold magenta]║  DeepAgent + Universal GEPA - Integration Test          ║[/]"
    )
    console.print(
        "[bold magenta]╚══════════════════════════════════════════════════════════╝[/]"
    )

    success = test_deepagent_gepa_integration()

    if success:
        console.print(
            "\n[green bold]🎉 DeepAgent is fully integrated with Universal GEPA![/]"
        )
        console.print("\n[cyan]Next steps:[/]")
        console.print(
            "   1. Install DeepAgent: cd reference/deepagents-master && pip install -e ."
        )
        console.print(
            "   2. Run optimization: super agent optimize my_agent --framework deepagent --auto light --reflection-lm gpt-4o"
        )
        console.print("   3. Test with real agents and see the results!")
        return 0
    else:
        console.print("\n[red bold]❌ Integration test failed[/]")
        return 1


if __name__ == "__main__":
    exit(main())
