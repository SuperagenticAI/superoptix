"""
Test script for OpenAI Agents SDK adapter.

This script tests the compilation of a SuperSpec playbook to OpenAI Agents SDK code.
"""

import yaml
from pathlib import Path
from superoptix.adapters.framework_registry import FrameworkRegistry


def test_openai_compilation():
    """Test OpenAI Agents SDK compilation."""
    print("=" * 80)
    print("Testing OpenAI Agents SDK Adapter")
    print("=" * 80)

    # Load a sample playbook
    playbook_path = Path("superoptix/agents/demo/observability_demo_playbook.yaml")
    print(f"\n📂 Loading playbook: {playbook_path}")

    with open(playbook_path) as f:
        playbook = yaml.safe_load(f)

    print(f"✅ Loaded playbook: {playbook['metadata']['name']}")

    # Test OpenAI Agents SDK compilation
    print("\n🚀 Compiling to OpenAI Agents SDK...")

    output_path = Path("/tmp/test_openai_agent.py")

    generated_path = FrameworkRegistry.compile_agent(
        framework="openai", playbook=playbook, output_path=str(output_path)
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

    assert Path(generated_path).exists()
    assert len(lines) > 0
