"""
Example: StackOne + Claude Agent SDK Integration via SuperOptiX Bridge
======================================================================

This example shows how to use StackOne tools with Claude Agent SDK's
in-process MCP server using the SuperOptiX StackOneBridge.

Features demonstrated:
- Converting StackOne tools to Claude SDK MCP format
- Creating in-process MCP server for tools
- Using tools with ClaudeAgentOptions
- Bidirectional session with ClaudeSDKClient
"""

import asyncio
import os
from dotenv import load_dotenv

# Try to import required packages
try:
    from stackone_ai import StackOneToolSet
    from claude_agent_sdk import (
        ClaudeAgentOptions,
        ClaudeSDKClient,
        query,
        AssistantMessage,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
    )
    from superoptix.adapters import StackOneBridge
except ImportError as e:
    print(f"Error: {e}")
    print("Please install required packages:")
    print("  pip install stackone-ai claude-agent-sdk superoptix")
    exit(1)

load_dotenv()


async def stackone_claude_sdk_integration():
    """Demonstrate StackOne + Claude Agent SDK integration using SuperOptiX bridge."""
    print("=" * 60)
    print("StackOne + Claude Agent SDK Integration via SuperOptiX")
    print("=" * 60)

    # 1. Initialize StackOne Toolset
    print("\n Step 1: Initializing StackOne Toolset...")
    toolset = StackOneToolSet()

    # 2. Fetch specific tools (e.g., HRIS employee management)
    account_id = os.getenv("STACKONE_ACCOUNT_ID", "test_account")
    print(f"   Fetching HRIS tools for account: {account_id}")

    tools = toolset.fetch_tools(
        include_tools=["hris_list_employees", "hris_get_employee"],
        account_ids=[account_id]
    )
    print(f"   Fetched {len(tools.to_list())} tools from StackOne")

    # 3. Use SuperOptiX Bridge to convert to Claude SDK MCP format
    print("\n Step 2: Converting tools using StackOneBridge...")
    bridge = StackOneBridge(tools)

    # Convert to Claude SDK in-process MCP server
    mcp_server, tool_names = bridge.to_claude_sdk()
    print(f"   Created MCP server with {len(tool_names)} tools")
    for name in tool_names:
        print(f"   - {name}")

    # 4. Create Claude Agent Options
    print("\n Step 3: Creating Claude Agent Options...")
    options = ClaudeAgentOptions(
        system_prompt="""You are an HR assistant with access to the company's HRIS system.
You can look up employee information, list employees, and provide helpful HR-related information.
Always use the available tools to fetch accurate data.""",
        mcp_servers={"stackone": mcp_server},
        allowed_tools=tool_names,
        model="claude-sonnet-4-5",
    )
    print("   Options configured with MCP server and tools")

    # 5. Execute a query
    print("\n Step 4: Running Claude Agent...")
    print("=" * 60)

    query_text = "List all employees in the engineering department"
    print(f"\n Query: {query_text}\n")

    # Use simple query() function
    async for message in query(prompt=query_text, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"\n[Tool Call: {block.name}]")
                    print(f"  Input: {block.input}")
        elif isinstance(message, ResultMessage):
            print(f"\n[Query completed - Cost: ${message.total_cost_usd:.4f}]")

    print("\n" + "=" * 60)
    print(" Integration Complete!")
    print("=" * 60)


async def stackone_claude_sdk_interactive():
    """
    Demonstrate interactive session with ClaudeSDKClient.

    This shows bidirectional conversation with tool access.
    """
    print("\n" + "=" * 60)
    print("Interactive Session with ClaudeSDKClient")
    print("=" * 60)

    # 1. Setup tools
    print("\n Setting up StackOne tools...")
    toolset = StackOneToolSet()
    account_id = os.getenv("STACKONE_ACCOUNT_ID", "test_account")

    tools = toolset.fetch_tools(
        include_tools=["hris_*"],
        account_ids=[account_id]
    )

    # 2. Convert to Claude SDK
    bridge = StackOneBridge(tools)
    mcp_server, tool_names = bridge.to_claude_sdk()

    # 3. Create options
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful HR assistant with HRIS access.",
        mcp_servers={"stackone": mcp_server},
        allowed_tools=tool_names,
    )

    # 4. Interactive session
    print("\n Starting interactive session...")
    print("   (This demonstrates multi-turn conversation)")

    async with ClaudeSDKClient(options=options) as client:
        # First query
        await client.query("How many employees do we have?")
        print("\n Query 1: How many employees do we have?")

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"  Claude: {block.text[:200]}...")
            elif isinstance(msg, ResultMessage):
                break

        # Follow-up query (uses conversation context)
        await client.query("Who is in the engineering team?")
        print("\n Query 2 (follow-up): Who is in the engineering team?")

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"  Claude: {block.text[:200]}...")
            elif isinstance(msg, ResultMessage):
                break

    print("\n Session ended.")


async def stackone_claude_sdk_with_discovery():
    """
    Demonstrate StackOne + Claude SDK with dynamic tool discovery.

    Uses meta-tools (tool_search, tool_execute) for large tool sets.
    """
    print("\n" + "=" * 60)
    print("Dynamic Tool Discovery with Claude SDK")
    print("=" * 60)

    # 1. Fetch all available tools
    print("\n Fetching all available tools...")
    toolset = StackOneToolSet()
    account_id = os.getenv("STACKONE_ACCOUNT_ID", "test_account")

    # Fetch broader set of tools
    tools = toolset.fetch_tools(
        include_tools=["hris_*", "ats_*", "crm_*"],
        account_ids=[account_id]
    )
    print(f"   Fetched {len(tools.to_list())} tools")

    # 2. Create discovery tools (only tool_search and tool_execute)
    print("\n Creating discovery meta-tools...")
    bridge = StackOneBridge(tools)
    mcp_server, tool_names = bridge.to_discovery_tools(framework="claude_sdk")
    print(f"   Created {len(tool_names)} meta-tools for dynamic discovery")

    # 3. Use with Claude
    options = ClaudeAgentOptions(
        system_prompt="""You are a smart business assistant with access to HRIS, ATS, and CRM tools.
You can dynamically search for and execute the right tool for any task.
First use tool_search to find relevant tools, then use tool_execute to run them.""",
        mcp_servers={"stackone": mcp_server},
        allowed_tools=tool_names,
    )

    print("\n The agent can now:")
    print("   1. Search for relevant tools using 'tool_search'")
    print("   2. Execute found tools using 'tool_execute'")
    print("\n   (Uncomment the query section to test)")

    # Uncomment to test:
    # async for message in query(prompt="Find tools for employee management", options=options):
    #     if isinstance(message, AssistantMessage):
    #         for block in message.content:
    #             if isinstance(block, TextBlock):
    #                 print(f"Claude: {block.text}")


async def main():
    """Run all examples."""
    # Run main integration example
    await stackone_claude_sdk_integration()

    # Run interactive session example (commented out - requires real API)
    # await stackone_claude_sdk_interactive()

    # Run discovery example
    await stackone_claude_sdk_with_discovery()


if __name__ == "__main__":
    asyncio.run(main())
