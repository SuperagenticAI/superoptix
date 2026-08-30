# SuperOptiX Harness

SuperOptiX includes a stateful harness runtime for running playbook-backed agents
without compiling a full pipeline first. It is the Python-first path for using
SuperOptiX as an agent harness: load project context, keep sessions, expose file
and shell tools through a sandbox policy, and run through a selected backend.

```bash
super harness run developer --prompt "Review this repository" --backend openai
super harness run developer --prompt "Return a typed answer" --backend pydantic-ai
super harness run developer --prompt "Research and patch" --backend deepagents --allow-write --allow-shell
super harness run developer --prompt "Fix failing tests" --backend codex --allow-write
super harness serve developer --backend codex --port 3583
```

## Backends

Supported harness backends:

- `openai` uses the OpenAI Agents SDK.
- `google-adk` uses Google ADK.
- `pydantic-ai` uses Pydantic AI.
- `deepagents` uses DeepAgents as the Python-native coding/research harness.
- `codex` uses the local Codex CLI coding-agent harness.

DSPy, CrewAI, and Microsoft Agent Framework are still supported by SuperOptiX's
existing compile/run/optimize pipeline where applicable, but they are not
SuperOptiX harness backends yet. The harness is intentionally focused on
frameworks that already expose a useful runtime agent loop, state model, or
coding-agent harness. For DSPy, CrewAI, and Microsoft, the current path remains:

```bash
super agent compile <agent> --framework dspy
super agent compile <agent> --framework crewai
super agent compile <agent> --framework microsoft
```

The Pydantic AI backend requires the `frameworks-pydantic-ai` extra:

```bash
pip install 'superoptix[frameworks-pydantic-ai]'
```

Run it from the CLI:

```bash
super harness run developer \
  --backend pydantic-ai \
  --provider openai \
  --model gpt-5.6-terra \
  --pydantic-request-limit 5 \
  --pydantic-tool-calls-limit 20 \
  --prompt "Analyze this API design and return a concise implementation plan"
```

Pydantic AI-specific controls:

- `--pydantic-request-limit`: maximum model requests in one run.
- `--pydantic-tool-calls-limit`: maximum tool calls in one run.
- `--pydantic-input-tokens-limit`: maximum input tokens in one run.
- `--pydantic-output-tokens-limit`: maximum output tokens in one run.
- `--pydantic-total-tokens-limit`: maximum total tokens in one run.
- `--pydantic-count-tokens-before-request`: ask Pydantic AI to count tokens
  before requests.
- `--pydantic-code-mode`: guarded optional hook for future Pydantic AI
  capability-based code execution. SuperOptiX checks the installed Pydantic AI
  Agent API before enabling it and fails clearly if capability support is not
  available.

The DeepAgents backend requires `deepagents>=0.5.6,<0.6.0`:

```bash
pip install 'superoptix[frameworks-deepagents]'
```

Run it from the CLI:

```bash
super harness run developer \
  --backend deepagents \
  --provider openai \
  --model gpt-5.6-terra \
  --deepagents-checkpointer memory \
  --allow-write \
  --allow-shell \
  --prompt "Inspect this repository and make the smallest safe fix"
```

DeepAgents-specific controls:

- `--deepagents-skill-source`: pass a DeepAgents skill source path. Repeatable.
  If omitted, SuperOptiX auto-detects `/.agents/skills` and `/skills` when they
  exist under the harness working directory.
- `--deepagents-memory`: pass a DeepAgents memory file such as `/AGENTS.md`.
  Repeatable. If omitted, SuperOptiX auto-detects `/AGENTS.md` and
  `/CLAUDE.md`.
- `--deepagents-checkpointer memory`: enable DeepAgents-managed in-memory
  session state.
- `--deepagents-debug`: enable DeepAgents debug mode.

SuperSpec can also pass native DeepAgents options under `spec.deepagents`:

```yaml
spec:
  deepagents:
    skills:
      - /.agents/skills
    memory:
      - /AGENTS.md
    checkpointer: memory
    debug: true
    subagents:
      - name: reviewer
        description: Reviews code changes for regressions.
        system_prompt: Review the repository changes and return concise findings.
```

The Codex backend requires a working `codex` binary on `PATH`, or an explicit
binary path:

```bash
super harness run developer \
  --backend codex \
  --codex-bin /opt/homebrew/bin/codex \
  --prompt "Inspect this repo"
```

The Codex backend is intentionally different from the `openai` and `google-adk`
backends. SuperOptiX starts the local Codex CLI harness with the selected model,
working directory, and sandbox mode. Codex then owns its own coding-agent loop,
file edits, command execution, approvals, and final answer generation.

## Sandboxes

For `openai`, `google-adk`, and `pydantic-ai`, SuperOptiX exposes built-in
file/search/shell tools through its local sandbox policy.

For `deepagents`, SuperOptiX adapts the same `LocalSandbox` into DeepAgents'
native backend contract. DeepAgents then uses its own built-in tools:
planning, filesystem access, shell execution, sub-agents, and context
management. `--allow-write` controls file write/edit capability through the
SuperOptiX sandbox. `--allow-shell` controls DeepAgents' `execute` tool.
SuperOptiX also passes DeepAgents filesystem permissions that mirror the
current sandbox policy, so the DeepAgents tool layer and the SuperOptiX backend
both enforce the same read/write intent.

For `codex`, sandboxing is delegated to Codex itself. SuperOptiX maps harness
flags to Codex sandbox modes:

- default: Codex `read-only`
- `--allow-write`: Codex `workspace-write`

`--allow-shell` does not add SuperOptiX shell tools to Codex. Codex manages its
own command execution and approvals inside its sandbox.

Docker, Vercel, E2B, Daytona, and similar systems should be treated as outer
execution environments: run SuperOptiX and Codex inside that environment, then
let Codex enforce the inner agent permissions.

Current local sandbox tools:

- `read`: read files or list directories.
- `grep`: search files.
- `glob`: find files.
- `write`: write files when the policy allows writes.
- `edit`: exact text replacement when the policy allows writes.
- `bash`: run commands when the policy allows shell access.

## Sessions

Harness sessions are persisted under `.superoptix/harness/sessions/<agent>/` by
default. Use `--session` to continue a named SuperOptiX harness session.

```bash
super harness run developer --backend codex --session fix-123 --prompt "Inspect failure"
super harness run developer --backend codex --session fix-123 --prompt "Implement fix" --allow-write
```

The HTTP service uses the same session id model:

```bash
super harness serve developer --backend codex --port 3583
curl http://localhost:3583/agents/developer/fix-123 \
  -H "content-type: application/json" \
  -d '{"prompt":"Review this repository"}'
```

## Context, Skills, and Roles

The harness discovers project instructions from:

- `AGENTS.md`
- `CLAUDE.md`
- `.agents/skills/*/SKILL.md`
- `.agents/skills/**/*.md`
- `roles/*.md`
- `.agents/roles/*.md`

Markdown skills can include YAML frontmatter for metadata. The Python API can
call `session.skill(...)`, and the CLI exposes `--skill` with repeatable
`--arg key=value` arguments.

Roles are loaded as instruction overlays. A role can be selected with
`--role <name>` or passed through the Python API.

## Python API

```python
from pathlib import Path

from superoptix.harness import HarnessAgent, LocalSandbox, SandboxPolicy

agent = HarnessAgent(
    name="developer",
    backend="deepagents",
    system_prompt="You are a coding agent.",
    cwd=Path.cwd(),
    sandbox=LocalSandbox(
        Path.cwd(),
        SandboxPolicy(allow_write=True, allow_shell=True),
    ),
    model_config={"provider": "openai", "model": "gpt-5.6-terra"},
)

session = await agent.session("fix-123")
result = await session.prompt("Find and fix the failing tests.")
print(result.text)
```

## Feature Comparison With Flue

This table compares the current SuperOptiX harness with Flue's public
agent-harness feature set.

| Feature | Flue | SuperOptiX harness today | Status |
| --- | --- | --- | --- |
| Built-in harness | Framework-level harness around agents, sessions, tools, sandboxes, and deployment. | Python harness package with CLI, service mode, sessions, tools, and backend adapters. | Implemented |
| Backend strategy | TypeScript runtime with provider model strings. | Multi-backend: OpenAI Agents SDK, Google ADK, Pydantic AI, DeepAgents, and Codex CLI. | Implemented |
| Compile-only frameworks | Not applicable. | DSPy, CrewAI, and Microsoft Agent Framework remain compile/run/optimize targets, not `super harness` backends. | Explicitly deferred |
| Markdown context | `AGENTS.md`, skills, and roles discovered at runtime. | `AGENTS.md`, `CLAUDE.md`, `.agents/skills`, and roles discovered at runtime. | Implemented |
| Skills | `session.skill(...)` with args, commands, role, model, and typed result. | `session.skill(...)` and CLI `--skill`; DeepAgents also receives skill source paths for native SkillsMiddleware. Per-skill command grants and CLI schema selection are not complete. | Partial |
| Roles | Agent, session, and call-level role overlays. | Role overlays through CLI and Python API. | Implemented |
| Tasks/subagents | First-class `session.task(...)`; child sessions share sandbox and can be exposed as a tool. | `session.task(...)` exists for Python API. DeepAgents brings its native `task` tool and accepts declarative subagents from `spec.deepagents.subagents`. Tool-exposed delegation is not wired uniformly for all backends. | Partial |
| Sessions/state | Platform store: memory on Node, durable Cloudflare store on Cloudflare, custom store support. | In-memory and file session stores; FastAPI route session ids. DeepAgents can use DeepAgents-managed in-memory session state. No SQLite/Postgres/Redis adapter yet. | Partial |
| Typed outputs | Valibot schema extraction. | Pydantic/TypeAdapter extraction in Python API; Pydantic AI backend supports framework-native usage limits. CLI schema flags are not added yet. | Partial |
| Local sandbox | Local filesystem sandbox and command execution. | Local sandbox policy with read/search/write/edit/bash gates for OpenAI, Google ADK, and Pydantic AI. DeepAgents gets the same sandbox through its native backend contract. | Implemented |
| Coding-agent sandbox | Virtual sandbox by default; external containers through sandbox factory/connectors. | Codex backend delegates to Codex sandbox modes. DeepAgents uses the SuperOptiX local sandbox adapter plus DeepAgents filesystem permissions. | Partial |
| Virtual sandbox | Lightweight in-process virtual sandbox by default. | Not implemented as a first-class SuperOptiX runtime. | Missing |
| Remote sandbox connectors | Connector interface for external sandboxes and examples such as container-backed coding agents. | Outer environments can run SuperOptiX, but Docker/Vercel/E2B/Daytona-style connectors are not first-class harness targets yet. | Missing |
| Command grants | Per-agent and per-call command registration with env handling. | Coarse `--allow-shell` and sandbox policy for local tools; Codex owns its own command flow. Pydantic AI can enforce request/tool/token limits. No `defineCommand` equivalent yet. | Partial |
| MCP tools | Runtime adapter for remote MCP tools. | Not wired into the harness runtime yet. | Missing |
| CLI run | `flue run`. | `super harness run`. | Implemented |
| Dev server | `flue dev` with rebuild/reload. | `super harness serve` exposes HTTP calls, but no file-watch rebuild loop. | Partial |
| Build/deploy | `flue build` for Node and Cloudflare Workers, plus deployment docs. | No `super harness build` target yet. | Missing |
| Webhooks | Generated `/agents/<name>/<id>` routes. | FastAPI `/agents/<name>/<session_id>` route. | Implemented |
| Streaming events | Node build supports SSE modes and runtime events. | No SSE/streaming endpoint yet. Codex backend captures final output. | Missing |
| Agent file routing | `.flue/agents/*.ts` and build-time trigger discovery. | SuperOptiX playbook discovery under `.super`; no harness-specific file-routing build target yet. | Partial |

## Roadmap

These items are planned for deeper harness parity and production deployment:

1. `super harness build`: generate deployable FastAPI, Cloud Run, Docker,
   Vercel, and GitHub Actions harness artifacts.
2. Managed outer sandboxes: first-class Docker, Vercel sandbox, E2B, Daytona, or
   equivalent adapters that run the whole harness in an isolated environment.
3. Virtual sandbox: a fast in-process filesystem/shell environment for simple
   high-throughput agents that do not need a full container.
4. Command grants: a Python equivalent of per-agent and per-skill command
   registration with scoped env/secrets.
5. MCP in the harness: connect remote MCP tools and pass them into the active
   backend without leaking secrets into prompts or files.
6. DeepAgents streaming integration: expose DeepAgents streaming directly
   instead of only final `ainvoke` output. In-memory DeepAgents session state
   exists, but durable stores are still pending.
7. Pydantic AI advanced capabilities: `--pydantic-code-mode` is available as an
   experimental switch, but advanced code-execution, guardrail, memory, and
   filesystem capability integrations are not enabled by default yet.
8. Codex App Server integration: use Codex through a programmatic protocol for
   streaming, thread mapping, events, and richer state instead of only
   subprocess `codex exec`.
9. Streaming HTTP: SSE or chunked event output for tool calls, task progress,
   and final results.
10. Durable stores: SQLite, Postgres, Redis, and cloud durable session adapters.
11. CLI typed output schemas: expose Pydantic result schemas from the CLI, not
   only the Python API.
12. Additional harness backends: DSPy, CrewAI, and Microsoft Agent Framework are
   intentionally deferred. They remain available through SuperOptiX's generated
   pipeline path instead of the stateful harness runtime.

## Positioning

Flue is a TypeScript agent harness framework with strong conventions around
Markdown, sessions, sandboxing, and build/deploy targets.

SuperOptiX is Python-first and multi-backend. The harness adds the same
framework-shaped entry point for Python projects, while keeping SuperOptiX's
existing strengths: SuperSpec playbooks, framework compilation, evaluation, and
optimization. The Pydantic AI backend is the typed Python service-agent path.
The DeepAgents backend is the Python-native batteries-included harness path.
The Codex backend is the local coding-agent path. OpenAI Agents SDK and Google
ADK remain available when users want those framework-native runtimes.
