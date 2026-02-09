<div align="center">
  <img src="logo.png" alt="SuperOptiX Logo" width="300" style="margin-bottom: -10px;"/>
  <h1 style="margin-top: 10px; margin-bottom: 10px;">SUPEROPTIX AI</h1>
  <h3 style="margin-top: 5px; margin-bottom: 15px;">Full Stack Agentic AI Optimization Framework</h3>
  <p style="margin-top: 10px; margin-bottom: 10px;"><strong>Evaluation-First ⚡ Optimization-Core 🕸️ Multi-Agent Orchestration</strong></p>
  <p style="margin-top: 5px; margin-bottom: 10px;"><em>Powered by DSPy. Refined by Superagentic AI.</em></p>
  <p style="margin-top: 10px; margin-bottom: 20px;">Build once with SuperSpec and compile to your preferred framework.</p>
</div>

<div align="center" style="margin: 30px 0;">
  <a href="quick-start/" style="background: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🚀 Quick Start</a>
  <a href="guides/golden-workflow/" style="background: #424242; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">⭐ Golden Workflow</a>
  <a href="guides/" style="background: #424242; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">📚 Guides</a>
  <a href="guides/framework-feature-matrix/" style="background: #424242; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">📊 Feature Matrix</a>
</div>

<div align="center" style="margin: 10px 0 24px 0;">
  <p style="margin: 8px 0;"><strong>Now supported:</strong> 🧪 RLM (Experimental) · 🗂️ StackOne Connectors · 🧬 GEPA Optimization</p>
  <p style="margin: 8px 0;">
    <a href="guides/rlm-experimental/">RLM Guide</a> ·
    <a href="guides/stackone-integration/">StackOne Guide</a> ·
    <a href="guides/multi-framework/">Framework Support</a>
  </p>
</div>

---

## What is SuperOptiX?

SuperOptiX is a universal agent optimization framework that lets you build, evaluate, and optimize agents across major frameworks with one workflow.

It keeps generated pipelines framework-native and readable in minimal mode, and enables full optimization lifecycle only when you opt in with `--optimize`.

---

## Core Workflow

```bash
# Pull agent
super agent pull developer

# Compile minimal pipeline
super agent compile developer --framework dspy

# Run
super agent run developer --framework dspy --goal "Design a migration plan"

# Optional optimization path
super agent compile developer --framework dspy --optimize
super agent optimize developer --framework dspy --auto light
```

---

## Why Teams Use It

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <tr>
    <td style="padding: 20px; border: 2px solid #2196F3; background: rgba(33, 150, 243, 0.08); vertical-align: top; width: 50%;">
      <h4 style="color: #2196F3; margin-top: 0;">🔬 Multi-Framework Freedom</h4>
      <ul>
        <li>Compile one SuperSpec into DSPy, OpenAI SDK, Claude SDK, Pydantic AI, CrewAI, Google ADK, DeepAgents</li>
        <li>Microsoft support remains available in legacy mode</li>
        <li>Switch frameworks without rewriting agent intent</li>
      </ul>
    </td>
    <td style="padding: 20px; border: 2px solid #4CAF50; background: rgba(76, 175, 80, 0.08); vertical-align: top; width: 50%;">
      <h4 style="color: #4CAF50; margin-top: 0;">🧬 Optimization by Default Path</h4>
      <ul>
        <li>Minimal runtime pipeline first</li>
        <li>GEPA optimization loop when needed</li>
        <li>BDD-style evaluation and repeatable quality checks</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td style="padding: 20px; border: 2px solid #FF9800; background: rgba(255, 152, 0, 0.08); vertical-align: top; width: 50%;">
      <h4 style="color: #FF9800; margin-top: 0;">🗂️ Connector-Driven Agents</h4>
      <ul>
        <li>StackOne integration for SaaS tool access</li>
        <li>Cross-framework connector compilation</li>
        <li>Clear connector demos including Calendly flows</li>
      </ul>
    </td>
    <td style="padding: 20px; border: 2px solid #9C27B0; background: rgba(156, 39, 176, 0.08); vertical-align: top; width: 50%;">
      <h4 style="color: #9C27B0; margin-top: 0;">🧪 RLM Support</h4>
      <ul>
        <li>Experimental RLM support in active integrations</li>
        <li>Fallback-friendly pipeline strategy</li>
        <li>Unified sandbox support coming soon</li>
      </ul>
    </td>
  </tr>
</table>

---

## Local and Cloud Routing

```bash
# Local Ollama
super agent run developer --framework dspy --local --provider ollama --model llama3.1:8b --goal "..."

# Cloud Google
super agent run developer --framework dspy --cloud --provider google-genai --model gemini-2.5-flash --goal "..."
```

---

## Next Steps

- [Golden Workflow](guides/golden-workflow.md)
- [Troubleshooting by Symptom](guides/troubleshooting-by-symptom.md)
- [Framework Feature Matrix](guides/framework-feature-matrix.md)
- [CLI Complete Guide](guides/cli-complete-guide.md)
