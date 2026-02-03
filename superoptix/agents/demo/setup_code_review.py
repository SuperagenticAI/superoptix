#!/usr/bin/env python3
"""
Setup script for Code Review Assistant

This script copies the knowledge base from the SuperOptiX package
to your project directory, making it easy to use the Code Review Assistant.

Usage:
    python setup_code_review.py

Or use the CLI command:
    super agent setup code_review_assistant
"""

import shutil
from pathlib import Path


def setup_code_review_assistant():
    """Copy knowledge base and dataset for Code Review Assistant."""

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  Code Review Assistant Setup                            ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    # Find SuperOptiX installation
    try:
        import superoptix

        package_root = Path(superoptix.__file__).parent
    except ImportError:
        print("❌ SuperOptiX not installed. Install with: pip install superoptix")
        return False

    # Find project root
    project_root = Path.cwd()
    super_file = project_root / ".super"

    if not super_file.exists():
        print("❌ Not in a SuperOptiX project directory.")
        print("   Run 'super init <project_name>' first.")
        return False

    print("✓ Found SuperOptiX installation")
    print("✓ In SuperOptiX project directory\n")

    # Step 1: Copy knowledge base
    print("📚 Step 1: Copying knowledge base...")

    source_knowledge = package_root / "knowledge" / "code_review"
    dest_knowledge = project_root / "knowledge" / "code_review"

    if not source_knowledge.exists():
        print(f"   ⚠️  Knowledge base not found at: {source_knowledge}")
        print("   ⚠️  Skipping knowledge base setup")
    else:
        # Create destination directory
        dest_knowledge.parent.mkdir(parents=True, exist_ok=True)

        # Copy entire directory
        if dest_knowledge.exists():
            print(f"   ⚠️  Knowledge base already exists at: {dest_knowledge}")
            response = input("   Overwrite? (y/N): ")
            if response.lower() != "y":
                print("   Skipping knowledge base copy")
            else:
                shutil.rmtree(dest_knowledge)
                shutil.copytree(source_knowledge, dest_knowledge)
                print(f"   ✅ Copied to: {dest_knowledge}")
        else:
            shutil.copytree(source_knowledge, dest_knowledge)
            print(f"   ✅ Copied to: {dest_knowledge}")

        # Count files
        knowledge_files = list(dest_knowledge.rglob("*.md"))
        print(f"   📄 {len(knowledge_files)} knowledge files copied")

    # Step 2: Pull dataset from marketplace
    print("\n📊 Step 2: Pulling dataset from marketplace...")

    source_dataset = package_root / "datasets" / "examples" / "code_review_examples.csv"
    dest_dataset = project_root / "data" / "code_review_examples.csv"

    if not source_dataset.exists():
        print(f"   ⚠️  Dataset not found at: {source_dataset}")
        print("   ⚠️  Skipping dataset setup")
    else:
        # Create data directory
        dest_dataset.parent.mkdir(parents=True, exist_ok=True)

        # Copy dataset
        if dest_dataset.exists():
            print(f"   ⚠️  Dataset already exists at: {dest_dataset}")
        else:
            shutil.copy(source_dataset, dest_dataset)
            print(f"   ✅ Copied to: {dest_dataset}")
            print(f"   💾 Size: {dest_dataset.stat().st_size / 1024:.1f} KB")

    # Step 3: Verify agent playbook
    print("\n📋 Step 3: Verifying agent playbook...")

    playbook_path = (
        project_root
        / "agents"
        / "code_review_assistant"
        / "playbook"
        / "code_review_assistant_playbook.yaml"
    )

    if not playbook_path.exists():
        print(f"   ⚠️  Agent playbook not found at: {playbook_path}")
        print("   💡 Pull the agent first: super agent pull code_review_assistant")
    else:
        print(f"   ✅ Found playbook at: {playbook_path}")

    # Summary
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  Setup Complete!                                        ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    print("📁 Files installed:")
    print("   • Knowledge base: knowledge/code_review/ (9 files)")
    print("   • Dataset: data/code_review_examples.csv (50+ examples)")

    print("\n🚀 Next steps:")
    print("   1. Compile the agent:")
    print("      super agent compile code_review_assistant")
    print("\n   2. Evaluate baseline:")
    print("      super agent evaluate code_review_assistant")
    print("\n   3. Optimize with GEPA:")
    print("      super agent optimize code_review_assistant --auto medium --fresh")
    print("\n   4. Re-evaluate:")
    print("      super agent evaluate code_review_assistant")
    print("\n   5. Run live:")
    print("      super agent run code_review_assistant")

    print("\n📖 Demo script: superoptix/agents/demo/ODSC_CODE_REVIEW_DEMO.md")
    print("\n✨ You're ready for ODSC!\n")

    return True


if __name__ == "__main__":
    setup_code_review_assistant()
