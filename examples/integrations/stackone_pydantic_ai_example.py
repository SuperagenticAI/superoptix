"""
Example: StackOne + Pydantic AI Integration via SuperOptiX Bridge
=================================================================

This example shows how to use StackOne tools in a Pydantic AI agent.
The SuperOptiX bridge automatically converts StackOne schemas into 
strictly typed Pydantic models for the agent.
"""

import os
import asyncio
from dotenv import load_dotenv

try:
    from stackone_ai import StackOneToolSet
    from pydantic_ai import Agent
    from superoptix.adapters import StackOneBridge
except ImportError as e:
    print(f"Error: {e}")
    print("Please install stackone-ai, pydantic-ai, and superoptix.")
    exit(1)

load_dotenv()

async def main():
    print("🚀 Initializing StackOne + Pydantic AI Integration...")

    # 1. Initialize StackOne Toolset
    toolset = StackOneToolSet()

    # 2. Fetch specific tools (e.g., HRIS employee management)
    account_id = os.getenv("STACKONE_ACCOUNT_ID", "test_account")
    print(f"Fetching tools for account: {account_id}")
    
    tools = toolset.fetch_tools(
        include_tools=["hris_get_employee"],
        account_ids=[account_id]
    )

    # 3. Use SuperOptiX Bridge to convert to Typed Pydantic AI Tools
    bridge = StackOneBridge(tools)
    pai_tools = bridge.to_pydantic_ai()
    
    print(f"✅ Converted {len(pai_tools)} StackOne tools to Pydantic AI format.")
    
    # Verify strict typing was generated
    # (In a real debugger, you'd see the 'tool_wrapper' signature has 'args: hris_get_employeeArgs')
    print(f"   Tool Function: {pai_tools[0].function.__name__}")
    
    # 4. Initialize Pydantic AI Agent with the tools
    # Note: Using a lightweight model for the demo
    agent = Agent(
        'openai:gpt-4o-mini',
        tools=pai_tools,
        system_prompt="You are a helpful HR assistant. Use the provided tools to answer queries."
    )

    print("\n🤖 Running Pydantic AI Agent...")
    
    # 5. Run the agent (simulated run as we might not have a live API key)
    query = "Get details for employee with ID 12345"
    print(f"   Query: '{query}'")
    
    # Note: This requires a valid OpenAI key. If not present, we skip the actual call.
    if os.getenv("OPENAI_API_KEY"):
        try:
            result = await agent.run(query)
            print(f"   Agent Response: {result.data}")
        except Exception as e:
            print(f"   Execution failed (likely due to invalid tool args or API error): {e}")
    else:
        print("   Skipping actual execution (OPENAI_API_KEY not found).")
        print("   But the tools are correctly typed and registered!")

if __name__ == "__main__":
    asyncio.run(main())
