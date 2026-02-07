"""
Example: StackOne + CrewAI Integration via SuperOptiX Bridge
=============================================================

This example shows how to use StackOne tools in a CrewAI agent
using the SuperOptiX StackOneBridge.

Features demonstrated:
- Converting StackOne tools to CrewAI format
- Using tools with CrewAI Agent
- Setting up a Crew with StackOne-powered tools
- Both sync and async tool support
"""

import os
from dotenv import load_dotenv

# Try to import required packages
try:
    from stackone_ai import StackOneToolSet
    from crewai import Agent, Task, Crew, Process
    from crewai.llm import LLM
    from superoptix.adapters import StackOneBridge
except ImportError as e:
    print(f"Error: {e}")
    print("Please install stackone-ai, crewai, and superoptix:")
    print("  pip install stackone-ai crewai superoptix")
    exit(1)

load_dotenv()


def stackone_crewai_integration():
    """Demonstrate StackOne + CrewAI integration using SuperOptiX bridge."""
    print("=" * 60)
    print("🚀 StackOne + CrewAI Integration via SuperOptiX")
    print("=" * 60)

    # 1. Initialize StackOne Toolset
    print("\n📦 Step 1: Initializing StackOne Toolset...")
    toolset = StackOneToolSet()

    # 2. Fetch specific tools (e.g., HRIS employee management)
    account_id = os.getenv("STACKONE_ACCOUNT_ID", "test_account")
    print(f"   Fetching HRIS tools for account: {account_id}")

    tools = toolset.fetch_tools(
        include_tools=["hris_list_employees", "hris_get_employee"],
        account_ids=[account_id]
    )
    print(f"   ✅ Fetched {len(tools.to_list())} tools from StackOne")

    # 3. Use SuperOptiX Bridge to convert to CrewAI format
    print("\n🔄 Step 2: Converting tools using StackOneBridge...")
    bridge = StackOneBridge(tools)

    # Option A: Standard sync tools
    crewai_tools = bridge.to_crewai()
    print(f"   ✅ Converted {len(crewai_tools)} tools to CrewAI format")

    # Option B: Async tools (for async workflows)
    # crewai_async_tools = bridge.to_crewai_async()

    # Print tool details
    for tool in crewai_tools:
        print(f"   - {tool.name}: {tool.description[:50]}...")

    # 4. Create CrewAI Agent with StackOne tools
    print("\n🤖 Step 3: Creating CrewAI Agent...")

    # Initialize LLM (uses OpenAI by default)
    llm = LLM(model="gpt-4o-mini")

    hr_agent = Agent(
        role="HR Assistant",
        goal="Help users with HR-related queries by fetching employee information",
        backstory="""You are an experienced HR assistant with access to the company's
        HRIS system. You can look up employee information, list employees, and
        provide helpful HR-related information.""",
        llm=llm,
        tools=crewai_tools,
        verbose=True,
        allow_delegation=False,
    )
    print("   ✅ Agent created with StackOne HRIS tools")

    # 5. Create a Task for the agent
    print("\n📋 Step 4: Creating Task...")
    hr_task = Task(
        description="List all employees in the engineering department and provide a summary.",
        expected_output="A summary of employees in the engineering department with their names and roles.",
        agent=hr_agent,
    )
    print("   ✅ Task created")

    # 6. Create a Crew
    print("\n👥 Step 5: Creating Crew...")
    crew = Crew(
        agents=[hr_agent],
        tasks=[hr_task],
        process=Process.sequential,
        verbose=True,
    )
    print("   ✅ Crew created")

    # 7. Execute (commented out for demo - uncomment to run)
    print("\n" + "=" * 60)
    print("🎉 Integration Complete!")
    print("=" * 60)
    print("\nTo run the crew, uncomment the following line:")
    print("   result = crew.kickoff()")
    print("\nThe CrewAI agent now has access to StackOne HRIS tools.")

    # Uncomment to actually run:
    # result = crew.kickoff()
    # print(f"\nResult: {result}")

    return crew


def stackone_crewai_with_discovery():
    """
    Demonstrate StackOne + CrewAI with dynamic tool discovery.

    This uses meta-tools (tool_search, tool_execute) instead of
    loading all tools upfront.
    """
    print("\n" + "=" * 60)
    print("🔍 StackOne + CrewAI with Dynamic Tool Discovery")
    print("=" * 60)

    # 1. Initialize StackOne Toolset with all tools
    print("\n📦 Fetching all available tools...")
    toolset = StackOneToolSet()
    account_id = os.getenv("STACKONE_ACCOUNT_ID", "test_account")

    # Fetch broader set of tools
    tools = toolset.fetch_tools(
        include_tools=["hris_*", "ats_*"],  # HRIS and ATS tools
        account_ids=[account_id]
    )
    print(f"   ✅ Fetched {len(tools.to_list())} tools")

    # 2. Create discovery tools (tool_search + tool_execute)
    print("\n🔄 Creating discovery meta-tools...")
    bridge = StackOneBridge(tools)
    discovery_tools = bridge.to_discovery_tools(framework="crewai")
    print(f"   ✅ Created {len(discovery_tools)} meta-tools (search + execute)")

    # 3. Create an agent that can dynamically find and use tools
    llm = LLM(model="gpt-4o-mini")

    discovery_agent = Agent(
        role="Smart HR & Recruiting Assistant",
        goal="Help with any HR or recruiting query by finding the right tool dynamically",
        backstory="""You are an intelligent assistant with access to a large toolbox.
        You can search for the right tool based on the task and execute it.
        Always search for the most appropriate tool before executing.""",
        llm=llm,
        tools=discovery_tools,
        verbose=True,
    )
    print("   ✅ Discovery agent created")

    print("\n" + "=" * 60)
    print("🎉 Dynamic Discovery Integration Complete!")
    print("=" * 60)
    print("\nThe agent can now:")
    print("  1. Search for relevant tools using 'tool_search'")
    print("  2. Execute found tools using 'tool_execute'")

    return discovery_agent


if __name__ == "__main__":
    # Run main integration example
    crew = stackone_crewai_integration()

    # Run discovery example
    discovery_agent = stackone_crewai_with_discovery()
