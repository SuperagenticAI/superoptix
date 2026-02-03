"""
Test script for CrewAI adapter.

This script tests the compilation of a SuperSpec playbook to CrewAI code.
"""

import yaml
from pathlib import Path
from superoptix.adapters.framework_registry import FrameworkRegistry


def test_crewai_compilation():
    """Test CrewAI compilation."""
    print("=" * 80)
    print("Testing CrewAI Adapter")
    print("=" * 80)

    # Load a sample playbook
    playbook_path = Path("superoptix/agents/demo/observability_demo_playbook.yaml")
    print(f"\n📂 Loading playbook: {playbook_path}")

    with open(playbook_path) as f:
        playbook = yaml.safe_load(f)

    print(f"✅ Loaded playbook: {playbook['metadata']['name']}")

    # Test CrewAI compilation
    print("\n🚀 Compiling to CrewAI...")

    output_path = Path("/tmp/test_crewai_agent.py")

    try:
        generated_path = FrameworkRegistry.compile_agent(
            framework="crewai", playbook=playbook, output_path=str(output_path)
        )

        print(f"✅ Compilation successful!")
        print(f"📄 Generated code: {generated_path}")

        # Show first 50 lines of generated code
        with open(generated_path) as f:
            lines = f.readlines()

        print(f"\n📋 First 50 lines of generated code:")
        print("-" * 80)
        for i, line in enumerate(lines[:50], 1):
            print(f"{i:3d} | {line}", end="")
        print("-" * 80)

        print(f"\n✅ Total lines generated: {len(lines)}")
        print(f"✅ File size: {Path(generated_path).stat().st_size} bytes")

        return True

    except Exception as e:
        print(f"\n❌ Compilation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_crewai_compilation()

    print("\n" + "=" * 80)
    if success:
        print("✅ TEST PASSED: CrewAI adapter works correctly!")
    else:
        print("❌ TEST FAILED: Check errors above")
    print("=" * 80)
