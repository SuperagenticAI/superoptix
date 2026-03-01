# RLM Support (Experimental)

SuperOptiX supports **RLM (Recursive Language Model)** as an optional reasoning layer.

## Current Scope

- RLM is **opt-in** (`enabled: true`).
- Existing agent runs are unchanged unless RLM is enabled.
- This guide covers: **DSPy**, **Pydantic AI**, and **Google ADK**.

## Install

```bash
# Native runtime
pip install "superoptix[rlm-native]"

# rlm_code provider
pip install "superoptix[rlm-code]"
```

## Native vs rlm_code (When To Use What)

| Framework | Config Path | Recommended Provider | Notes |
| --- | --- | --- | --- |
| DSPy | `spec.dspy.rlm` | `native` | Uses DSPy-native `dspy.RLM` path; keep this as default. |
| Pydantic AI | `spec.pydantic_ai.rlm` | `native` first, `rlm_code` when you want RLM Code runtime behavior | `rlm_code` is supported as an opt-in provider. |
| Google ADK | `spec.google_adk.rlm` | `native` | Keep native for now; `rlm_code` is accepted in schema but should be treated as preview/fallback territory. |

Provider values:
- `native`: default runtime.
- `legacy`: alias to `native`.
- `rlm_code`: opt-in provider (`rlm-code` package required).

## RLM Modes

- `assist`: RLM draft + framework execution.
- `replace`: RLM-only response (framework call skipped).
- `auto`: dynamic mode selection:
  - long prompt (`>= auto_long_context_chars`) -> `replace`
  - short prompt -> `direct` or `assist` via `auto_short_context_mode`

## Key Fields

```yaml
rlm:
  enabled: true
  provider: native                 # native | legacy | rlm_code
  mode: auto                       # assist | replace | auto
  auto_long_context_chars: 12000
  auto_short_context_mode: direct  # direct | assist

  backend: litellm
  environment: python
  max_iterations: 8
  max_depth: 1
  verbose: false
  persistent: false
  task_model: ""
  api_key_env: ""
  api_base: ""
  logger:
    enabled: false
    log_dir: .superoptix/logs/rlm
    file_name: rlm
```

## Examples

DSPy (native):

```yaml
spec:
  dspy:
    rlm:
      enabled: true
      max_iters: 10
      max_llm_calls: 5
```

Pydantic AI (rlm_code opt-in):

```yaml
spec:
  pydantic_ai:
    rlm:
      enabled: true
      provider: rlm_code
      mode: assist
      backend: litellm
      max_iterations: 8
```

Google ADK (native):

```yaml
spec:
  google_adk:
    rlm:
      enabled: true
      provider: native
      mode: auto
```
