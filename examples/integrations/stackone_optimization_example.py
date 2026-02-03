"""
Example: Optimizing StackOne Tool Descriptions with GEPA
========================================================

This example shows how to use SuperOptiX's GEPA engine to automatically
improve the descriptions of StackOne tools for better LLM performance.
"""

import os
from dotenv import load_dotenv
from superoptix.adapters import StackOneBridge

# Mock or real StackOne setup
try:
    from stackone_ai import StackOneToolSet
except ImportError:
    print("Please install stackone-ai.")
    exit(1)

load_dotenv()

def simple_metric(gold, pred, trace=None):
    """Simple metric: checks if the tool was called correctly."""
    # In a real scenario, this would evaluate if the LLM successfully 
    # used the tool based on the description.
    return 1.0 if "result" in pred else 0.0

def stackone_optimization_demo():
    print("🧬 Starting StackOne Tool Description Optimization...")

    # 1. Initialize StackOne
    toolset = StackOneToolSet()
    
    # 2. Fetch tools to optimize
    tools = toolset.fetch_tools(
        include_tools=["hris_get_employee"],
        account_ids=[os.getenv("STACKONE_ACCOUNT_ID", "test_account")]
    )
    
    # 3. Define a small training dataset
    # These represent user queries that the tool should answer
    dataset = [
        {
            "inputs": {"query": "Get details for employee with ID 123"},
            "outputs": {"id": "123"}
        },
        {
            "inputs": {"query": "Find information about worker emp_456"},
            "outputs": {"id": "emp_456"}
        }
    ]

    # 4. Use SuperOptiX Bridge to optimize
    bridge = StackOneBridge(tools)
    
    print(f"Original Description: {tools[0].description}")
    
    # Run GEPA optimization
    # This will use the reflection model to rewrite the description
    optimized_tools = bridge.optimize(
        dataset=dataset,
        metric=simple_metric,
        reflection_lm="gpt-4o-mini",
        max_iterations=3
    )

    print("\n✨ Optimization Complete!")
    print(f"Optimized Description: {optimized_tools[0].description}")

if __name__ == "__main__":
    stackone_optimization_demo()
