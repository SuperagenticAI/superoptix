"""
Example: StackOne Dynamic Tool Discovery with DSPy
==================================================

This example shows how to use the 'Discovery Mode'. Instead of loading 
100+ tools into the agent context, we give the agent just 2 tools:
1. tool_search: To find the right tool.
2. tool_execute: To run the tool.

This allows agents to navigate the entire StackOne ecosystem dynamically.
"""

import os
import dspy
from dotenv import load_dotenv

try:
    from stackone_ai import StackOneToolSet
    from superoptix.adapters import StackOneBridge
except ImportError:
    print("Please install stackone-ai, dspy, and superoptix.")
    exit(1)

load_dotenv()

# Setup DSPy
lm = dspy.LM('openai/gpt-4o')
dspy.configure(lm=lm)

def main():
    print("🚀 Initializing StackOne Dynamic Discovery Agent...")

    # 1. Initialize StackOne Toolset
    # We fetch ALL tools (or a large subset) because we aren't loading them into the LLM context directly
    toolset = StackOneToolSet()
    
    account_id = os.getenv("STACKONE_ACCOUNT_ID", "test_account")
    print("Fetching ALL available tools for index...")
    
    # In a real app, you might cache this
    all_tools = toolset.fetch_tools(account_ids=[account_id])
    print(f"✅ Loaded {len(all_tools.to_list())} tools into the search index.")

    # 2. Create Discovery Bridge
    bridge = StackOneBridge(all_tools)
    
    # 3. Get Discovery Tools (Only 'tool_search' and 'tool_execute')
    # These are small enough to fit in any context window
    discovery_tools = bridge.to_discovery_tools(framework="dspy")
    
    print(f"✅ Agent equipped with {len(discovery_tools)} meta-tools: {[t.name for t in discovery_tools]}")

    # 4. Create a ReAct Agent
    # The agent must figure out it needs to search first, then execute
    agent = dspy.ReAct("question -> answer", tools=discovery_tools)

    print("\n🤖 Running Agent with Dynamic Discovery...")
    print("   Goal: Find employee details for ID 12345 (Agent doesn't know the tool name yet!)")
    
    # In a real run with a smart model (GPT-4o), the trace would look like:
    # 1. Thought: I need to find a tool to get employee details.
    # 2. Action: tool_search(query=\"get employee details\")
    # 3. Observation: Found 'hris_get_employee'
    # 4. Thought: I should use hris_get_employee.
    # 5. Action: tool_execute(toolName=\"hris_get_employee\", params={\"id\": \"12345\"})
    
    # response = agent(question="Get details for employee ID 12345")
    # print(f"Response: {response.answer}")
    
    print("\n✅ Discovery setup complete. The agent can now dynamically find and use any of the loaded tools.")

if __name__ == "__main__":
    main()
