"""
Example: StackOne + DSPy Integration via SuperOptiX Bridge
=========================================================

This example shows how to use StackOne tools in a DSPy program
using the SuperOptiX StackOneBridge.
"""

import os
from dotenv import load_dotenv

# Try to import stackone and dspy
try:
    from stackone_ai import StackOneToolSet
    import dspy
    from superoptix.adapters import StackOneBridge
except ImportError as e:
    print(f"Error: {e}")
    print("Please install stackone-ai, dspy, and superoptix.")
    exit(1)

load_dotenv()

# Setup DSPy model
# Note: Ensure you have OPENAI_API_KEY in your .env
lm = dspy.LM('openai/gpt-4o-mini')
dspy.configure(lm=lm)

def stackone_dspy_integration():
    print("🚀 Initializing StackOne + DSPy Integration...")

    # 1. Initialize StackOne Toolset
    toolset = StackOneToolSet()

    # 2. Fetch specific tools (e.g., HRIS employee management)
    # Note: Replace with a valid account ID if testing for real
    account_id = os.getenv("STACKONE_ACCOUNT_ID", "test_account")
    print(f"Fetching tools for account: {account_id}")
    
    tools = toolset.fetch_tools(
        include_tools=["hris_get_employee"],
        account_ids=[account_id]
    )

    # 3. Use SuperOptiX Bridge to convert to DSPy
    bridge = StackOneBridge(tools)
    dspy_tools = bridge.to_dspy()
    
    print(f"✅ Converted {len(dspy_tools)} StackOne tools to DSPy format.")

    # 4. Use in a DSPy ReAct agent
    # This is a standard DSPy ReAct agent that now has access to StackOne SaaS tools
    agent = dspy.ReAct("name -> employee_details", tools=dspy_tools)

    print("\n🤖 Running DSPy Agent with StackOne tools...")
    # This is a simulation - in a real run, the agent would call the tool
    # result = agent(name="John Doe")
    # print(f"Result: {result}")
    
    print("\nIntegration Complete! The DSPy agent is now ready to use StackOne tools.")

if __name__ == "__main__":
    stackone_dspy_integration()
