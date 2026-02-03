"""
Example: StackOne + Microsoft Semantic Kernel Integration via SuperOptiX Bridge
===============================================================================

This example shows how to import StackOne tools as a Semantic Kernel Plugin.
"""

import asyncio
import os
from dotenv import load_dotenv

try:
    from stackone_ai import StackOneToolSet
    from superoptix.adapters import StackOneBridge
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
except ImportError as e:
    print(f"Error: {e}")
    print("Please install stackone-ai, semantic-kernel, and superoptix.")
    exit(1)

load_dotenv()


async def main():
    print("🚀 Initializing StackOne + Semantic Kernel Integration...")

    # 1. Initialize StackOne Toolset
    toolset = StackOneToolSet()

    account_id = os.getenv("STACKONE_ACCOUNT_ID", "test_account")
    tools = toolset.fetch_tools(
        include_tools=["hris_get_employee"], account_ids=[account_id]
    )

    # 2. Use SuperOptiX Bridge to convert to Kernel Functions
    bridge = StackOneBridge(tools)
    sk_functions = bridge.to_semantic_kernel()

    print(
        f"✅ Converted {len(sk_functions)} StackOne tools to Semantic Kernel Functions."
    )

    # 3. Initialize Kernel
    kernel = sk.Kernel()

    # Add OpenAI Service (optional for this demo, but needed for real execution)
    if os.getenv("OPENAI_API_KEY"):
        service_id = "default"
        kernel.add_service(
            OpenAIChatCompletion(service_id=service_id, ai_model_id="gpt-4o-mini")
        )

    # 4. Register Functions as a Plugin
    # We add each converted function to the kernel
    plugin_name = "StackOneHRIS"
    for func in sk_functions:
        kernel.add_function(plugin_name=plugin_name, function=func)

    print(f"✅ Registered plugin '{plugin_name}' with kernel.")

    # 5. Invoke a function manually (Simulating Planner usage)
    # Get the function
    func_name = sk_functions[0].name
    sk_func = kernel.get_function(plugin_name, func_name)

    print(f"\n🤖 Invoking function '{func_name}'...")

    # In a real scenario with a Planner, the Planner would call this.
    # Here we invoke directly for demonstration.
    try:
        # Note: This will fail if no real API key is present for StackOne
        # We wrap in try/catch to show the flow
        result = await kernel.invoke(sk_func, id="12345")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Execution attempted (success implies integration worked): {e}")


if __name__ == "__main__":
    asyncio.run(main())
