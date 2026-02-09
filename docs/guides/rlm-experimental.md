# RLM Support (Experimental)

SuperOptiX supports **RLM (Recursive Language Model)** workflows as an experimental capability.

## Status

- RLM support is available in active framework integrations where configured.
- The API and behavior may evolve while we stabilize cross-framework ergonomics.
- **Unified sandbox support for RLM is coming soon.**

## What This Means for Users

- You can start testing RLM flows today in supported pipelines.
- Expect ongoing improvements in defaults, tracing, and guardrails.
- For stable production workloads, keep a non-RLM fallback path in your playbook.

## Recommended Usage

- Start with small prompts and short iterations.
- Keep model settings conservative while tuning.
- Validate output with scenarios before enabling broader usage.

## Related Guides

- [Multi-Framework Support](multi-framework.md)
- [DSPy Optimizers](dspy-optimizers.md)
- [GEPA Optimization](gepa-optimization.md)
