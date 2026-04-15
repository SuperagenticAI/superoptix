# OpenAI Agents SDK in SuperOptiX

SuperOptiX now supports the newer OpenAI Agents SDK model for production-style agent execution, including harness + sandbox patterns.

This guide explains what it means for users and how to use it in day-to-day workflows.

## What You Get

- Cleaner separation between agent logic and execution environment.
- Better support for long-running, tool-using workflows.
- Sandbox-ready execution model when you want isolated file/compute access.
- Same SuperOptiX workflow for compile, evaluate, optimize, and run.

## Who This Is For

Use this if you are building agents in SuperOptiX with the OpenAI framework and want:

- safer execution boundaries,
- easier production migration,
- and a consistent optimization workflow.

## Quick Start

1. Install/update dependencies with OpenAI support.
2. Compile your agent for `openai`.
3. Run evaluation and optimization as usual.
4. Enable sandbox config in your SuperSpec when you are ready.

## SuperSpec Pattern

Use `openai_agent` for OpenAI-specific runtime behavior.  
Keep sandbox optional so you can start simple and enable it when needed.

```yaml
openai_agent:
  sandbox:
    enabled: false
```

When you have sandbox infrastructure available, switch `enabled` to `true` and add your sandbox manifest inputs/outputs according to your environment policy.

## Recommended Workflow

1. `super agent compile <agent_name> --framework openai`
2. `super agent evaluate <agent_name>`
3. `super agent optimize <agent_name> --framework openai`
4. `super agent evaluate <agent_name>`
5. `super agent run <agent_name> --goal "<task>"`

This keeps optimization grounded in measurable BDD behavior before production use.

## Sandbox or No Sandbox?

- If you do not have sandbox infrastructure yet, keep sandbox disabled and continue normally.
- If you need stricter isolation and controlled execution, enable sandbox and configure mounts/permissions for your environment.

Both paths use the same SuperOptiX authoring and optimization flow.

## Best Practices

- Start with clear BDD scenarios in playbooks.
- Optimize only after baseline evaluation.
- Enable sandbox for workloads that touch files, tools, or sensitive data boundaries.
- Keep prompts, tools, and expected outputs aligned with measurable scenarios.

## Related Guides

- [OpenAI SDK Integration](openai-sdk-integration.md)
- [SuperSpec Guide](superspec.md)
- [Framework Feature Matrix](framework-feature-matrix.md)
