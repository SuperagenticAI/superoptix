# StackOne + Claude Agent SDK Guide

This guide explains how to run StackOne tools through Claude Agent SDK using SuperOptiX's `StackOneBridge`.

## What This Integration Does

- Converts StackOne tools into Claude SDK `SdkMcpTool` objects.
- Bundles them into one in-process MCP server using `create_sdk_mcp_server(...)`.
- Returns Claude-compatible allowed tool names (`mcp__stackone__<tool_name>`).
- Supports discovery mode (`tool_search`, `tool_execute`) for large tool inventories.

## Install

```bash
pip install superoptix stackone-ai claude-agent-sdk
```

If you installed SuperOptiX in editable mode:

```bash
pip install -e ".[frameworks-claude-sdk]"
```

## Authentication

Claude Agent SDK needs Anthropic auth at runtime:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Optional advanced endpoint override:

```bash
export ANTHROPIC_BASE_URL="https://your-anthropic-compatible-endpoint"
```

## Recommended Claude Models

Use current model aliases from Anthropic's model overview:

- `claude-opus-4-5`
- `claude-sonnet-4-5`
- `claude-haiku-4-5`

Latest snapshot IDs:

- `claude-opus-4-5-20251101`
- `claude-sonnet-4-5-20250929`
- `claude-haiku-4-5-20251001`

## End-to-End Example

```python
import asyncio
from stackone_ai import StackOneToolSet
from claude_agent_sdk import ClaudeAgentOptions, query
from superoptix.adapters import StackOneBridge


async def main():
    toolset = StackOneToolSet()
    tools = toolset.fetch_tools(
        include_tools=["hris_list_employees", "hris_get_employee"],
        account_ids=["your_stackone_account_id"],
    )

    bridge = StackOneBridge(tools)
    mcp_server, tool_names = bridge.to_claude_sdk()

    options = ClaudeAgentOptions(
        system_prompt="You are an HR assistant. Use tools for factual answers.",
        mcp_servers={"stackone": mcp_server},
        allowed_tools=tool_names,
        model="claude-sonnet-4-5",
    )

    async for message in query(
        prompt="List all employees in engineering", options=options
    ):
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
```

## Discovery Mode (Large Tool Catalogs)

If you have many tools, inject only two meta-tools and let the agent discover dynamically:

```python
mcp_server, tool_names = StackOneBridge(tools).to_discovery_tools(framework="claude_sdk")
```

This gives the model:

- `tool_search`: find the best tool
- `tool_execute`: execute by name with args

## How SuperOptiX Playbook Should Look

```yaml
spec:
  language_model:
    location: cloud
    provider: anthropic
    model: claude-sonnet-4-5
    temperature: 0.2
```

SuperOptiX compile/run guidance intentionally asks users to edit this playbook directly and recompile, rather than mutating pulled templates automatically.

## Troubleshooting

- `Claude SDK authentication is not configured`:
  Set `ANTHROPIC_API_KEY` in the shell where you run `super`.
- `provider='anthropic' expects a Claude model`:
  Replace model with one of the IDs above and recompile.
- `Task exception ... cancel scope`:
  Use latest generated pipeline; SuperOptiX now avoids early stream termination.

## References

- Anthropic model overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Claude SDK auth: https://github.com/anthropics/claude-code-sdk-python?tab=readme-ov-file#authentication
