---
title: Introduction - SuperOptiX AI
---

<div align="center">
  <img src="../logo.png" alt="SuperOptiX Logo" width="200" style="margin-bottom: 10px;"/>
  <h1 style="margin-top: 10px; margin-bottom: 10px;">Introduction to SuperOptiX</h1>
  <p style="margin-top: 10px; margin-bottom: 20px;"><strong>The world's first universal agent optimization framework</strong></p>
    </div>
    
<div align="center" style="margin: 30px 0;">
  <a href="../quick-start/" style="background: #4CAF50; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🚀 Quick Start</a>
  <a href="../setup/" style="background: #2196F3; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">⚙️ Setup Guide</a>
  <a href="../guides/gepa-optimization/" style="background: #FF9800; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🧬 GEPA Optimizer</a>
  <a href="../guides/multi-framework/" style="background: #9C27B0; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🔬 Framework Guide</a>
    </div>
    
---

## 🔍 What is SuperOptiX?

SuperOptiX is the **world's first universal agent optimization framework** that brings end-to-end optimization to AI agents across **6 major frameworks**. Build, evaluate, and optimize agents from any framework with a unified workflow powered by GEPA (Genetic-Pareto Algorithm).

Unlike most frameworks that bolt on evals and monitoring as an afterthought, SuperOptiX makes **evaluation, optimization, and guardrails core to the development lifecycle**. Whether you're using DSPy, OpenAI SDK, CrewAI, Google ADK, Microsoft, or DeepAgents, SuperOptiX gives you the power to optimize and deploy production-grade agents.

SuperOptiX brings together declarative agent specification, universal GEPA optimization, built-in evaluation, multi-framework support, and multi-agent orchestration, all grounded in the principles of test-driven development and context engineering.

## Core Philosophy

Unlike frameworks that lock you into a single approach, SuperOptiX gives you **freedom of choice with consistency of experience**. Build agents in DSPy, OpenAI SDK, CrewAI, Google ADK, Microsoft Agent Framework, or DeepAgents, then optimize them all with the same powerful GEPA optimizer.

!!! abstract "Key Principle"
    Declarative by Design. Universally Optimized. Framework-Agnostic.

With its native DSL (SuperSpec), GEPA optimization engine, support for 6 major frameworks, structured agent tiers (Oracles, Genies, Protocols, Superagents, Sovereigns), and full-stack abstractions, SuperOptiX empowers you to build reliable, adaptive, and intelligent agentic systems without vendor lock-in.

---

## 🔮 Future-Proof by Design

SuperOptiX provides true extensibility across three critical abstraction layers:

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <tr>
    <td style="padding: 20px; border: 2px solid #2196F3; background: rgba(33, 150, 243, 0.08); vertical-align: top; width: 33%;">
      <h4 style="color: #2196F3; margin-top: 0;">🔬 Framework Layer</h4>
      <p><strong>Swap AI frameworks on demand</strong></p>
      <p>Currently supported: DSPy, OpenAI SDK, CrewAI, Google ADK, Microsoft Agent Framework, DeepAgents</p>
      <p><strong>Future ready:</strong> New framework? Add an adapter. Your agents keep working.</p>
      <pre style="background: rgba(0,0,0,0.05); padding: 8px; border-radius: 4px; margin-top: 10px; font-size: 0.85em;">target_framework: any_framework</pre>
    </td>
    <td style="padding: 20px; border: 2px solid #9C27B0; background: rgba(156, 39, 176, 0.08); vertical-align: top; width: 33%;">
      <h4 style="color: #9C27B0; margin-top: 0;">🔌 Protocol Layer</h4>
      <p><strong>Swap communication protocols</strong></p>
      <p>Currently supported: MCP (Model Context Protocol)</p>
      <p><strong>Future ready:</strong> A2A, custom protocols. Protocol-first design means seamless adoption.</p>
      <pre style="background: rgba(0,0,0,0.05); padding: 8px; border-radius: 4px; margin-top: 10px; font-size: 0.85em;">protocol: mcp | a2a | custom</pre>
    </td>
    <td style="padding: 20px; border: 2px solid #FF9800; background: rgba(255, 152, 0, 0.08); vertical-align: top; width: 33%;">
      <h4 style="color: #FF9800; margin-top: 0;">🧬 Optimizer Layer</h4>
      <p><strong>Swap optimization engines</strong></p>
      <p>Currently supported: GEPA, DSPy optimizers (BootstrapFewShot, MIPRO, MIPROv2)</p>
      <p><strong>Future ready:</strong> New optimizer research? Plugin system makes integration trivial.</p>
      <pre style="background: rgba(0,0,0,0.05); padding: 8px; border-radius: 4px; margin-top: 10px; font-size: 0.85em;">optimizer: gepa | mipro | custom</pre>
    </td>
  </tr>
</table>

<div align="center" style="margin: 30px 0; padding: 25px; background: linear-gradient(135deg, rgba(33, 150, 243, 0.08) 0%, rgba(156, 39, 176, 0.08) 50%, rgba(255, 152, 0, 0.08) 100%); border-radius: 8px; border: 2px solid rgba(33, 150, 243, 0.2);">
  <h4 style="margin-top: 0; color: #2196F3;">💎 Abstraction Without Lock-In</h4>
  <p style="margin: 10px 0; font-size: 1.05em;">Your agent context stays constant. Frameworks evolve. Protocols emerge. Optimizers improve.</p>
  <p style="margin: 10px 0; font-size: 1.05em;"><strong>SuperOptiX adapts without breaking your agents.</strong></p>
  <p style="margin: 15px 0 0 0; font-size: 0.95em; opacity: 0.9;">Built for today. Ready for tomorrow. Future-proof forever.</p>
</div>

---

## 🏗️ Full-Stack Agentic Optimization

SuperOptiX provides **end-to-end optimization across every layer of the agentic stack**. While other frameworks optimize prompts in isolation, SuperOptiX takes a holistic approach with universal GEPA optimization that works independently of any specific framework:

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <tr>
    <td style="padding: 20px; border: 2px solid #4CAF50; background: rgba(76, 175, 80, 0.06); vertical-align: top; width: 25%;">
      <h4 style="color: #4CAF50; margin-top: 0;">💬 Prompts & Instructions</h4>
      <p style="font-size: 0.95em;">Evolutionary optimization of:</p>
      <ul style="font-size: 0.9em; margin: 10px 0;">
        <li>System prompts</li>
        <li>Agent instructions</li>
        <li>Reasoning patterns</li>
        <li>Task descriptions</li>
      </ul>
    </td>
    <td style="padding: 20px; border: 2px solid #2196F3; background: rgba(33, 150, 243, 0.06); vertical-align: top; width: 25%;">
      <h4 style="color: #2196F3; margin-top: 0;">📚 RAG & Retrieval</h4>
      <p style="font-size: 0.95em;">Context optimization across:</p>
      <ul style="font-size: 0.9em; margin: 10px 0;">
        <li>Retrieval queries</li>
        <li>Chunking strategies</li>
        <li>Embedding selection</li>
        <li>Relevance scoring</li>
      </ul>
    </td>
    <td style="padding: 20px; border: 2px solid #FF9800; background: rgba(255, 152, 0, 0.06); vertical-align: top; width: 25%;">
      <h4 style="color: #FF9800; margin-top: 0;">🛠️ Tools & Functions</h4>
      <p style="font-size: 0.95em;">MCP protocol optimization for:</p>
      <ul style="font-size: 0.9em; margin: 10px 0;">
        <li>Tool selection</li>
        <li>Parameter tuning</li>
        <li>Execution strategies</li>
        <li>Error handling</li>
      </ul>
    </td>
    <td style="padding: 20px; border: 2px solid #9C27B0; background: rgba(156, 39, 176, 0.06); vertical-align: top; width: 25%;">
      <h4 style="color: #9C27B0; margin-top: 0;">🧠 Memory & Context</h4>
      <p style="font-size: 0.95em;">Intelligent optimization of:</p>
      <ul style="font-size: 0.9em; margin: 10px 0;">
        <li>Memory retrieval</li>
        <li>Context windows</li>
        <li>Storage strategies</li>
        <li>Attention patterns</li>
      </ul>
    </td>
  </tr>
</table>

<div align="center" style="margin: 25px 0; padding: 25px; background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(33, 150, 243, 0.1) 33%, rgba(255, 152, 0, 0.1) 66%, rgba(156, 39, 176, 0.1) 100%); border-radius: 8px; border: 2px solid rgba(76, 175, 80, 0.4);">
  <h4 style="margin-top: 0; color: #4CAF50;">⚡ Universal Optimization Engine</h4>
  <p style="margin: 10px 0; font-size: 1.05em;"><strong>Framework-agnostic optimization</strong> means GEPA works the same whether you're using DSPy, CrewAI, OpenAI SDK, or any other framework.</p>
  <p style="margin: 10px 0; font-size: 1.05em;">No framework-specific tricks. No vendor lock-in. Just pure, portable optimization across your entire agentic stack.</p>
  <p style="margin: 15px 0 0 0; font-size: 0.95em; opacity: 0.9;"><strong>Optimize everything. Switch anything. Break nothing.</strong></p>
</div>

---

## ⚡ Core Features

<table style="width: 100%; border-collapse: collapse;">
  <tr>
    <td style="padding: 20px; width: 50%; vertical-align: top; border: 2px solid rgba(33, 150, 243, 0.3); background: rgba(33, 150, 243, 0.05);">
      <h3 style="color: #2196F3;">🎯 Evaluation-First Architecture</h3>
      <p>RSpec-style BDD specifications with built-in testing and validation from day one. Define behavior scenarios, run automated evaluations, track metrics across optimization iterations.</p>
    </td>
    <td style="padding: 20px; width: 50%; vertical-align: top; border: 2px solid rgba(76, 175, 80, 0.3); background: rgba(76, 175, 80, 0.05);">
      <h3 style="color: #4CAF50;">🧬 GEPA Universal Optimizer</h3>
      <p>Automatic optimization across all 6 major agent frameworks with proven results. Achieve 37.5% → 80% improvements with just 3-10 training scenarios.</p>
    </td>
  </tr>
  <tr>
    <td style="padding: 20px; width: 50%; vertical-align: top; border: 2px solid rgba(255, 152, 0, 0.3); background: rgba(255, 152, 0, 0.05);">
      <h3 style="color: #FF9800;">🔬 Multi-Framework Support</h3>
      <p>Works with DSPy, OpenAI SDK, CrewAI, Google ADK, Microsoft, and DeepAgents. One workflow, six frameworks, unlimited possibilities.</p>
    </td>
    <td style="padding: 20px; width: 50%; vertical-align: top; border: 2px solid rgba(156, 39, 176, 0.3); background: rgba(156, 39, 176, 0.05);">
      <h3 style="color: #9C27B0;">📝 SuperSpec DSL</h3>
      <p>Declarative language for agent specifications with Kubernetes-style versioning. Write once, deploy to any framework.</p>
    </td>
  </tr>
  <tr>
    <td style="padding: 20px; width: 50%; vertical-align: top; border: 2px solid rgba(33, 150, 243, 0.3); background: rgba(33, 150, 243, 0.05);">
      <h3 style="color: #2196F3;">🧠 Context Engineering</h3>
      <p>Systematic approach to delivering optimal information and tools to agents. Includes RAG, MCP protocol, and memory optimization.</p>
    </td>
    <td style="padding: 20px; width: 50%; vertical-align: top; border: 2px solid rgba(76, 175, 80, 0.3); background: rgba(76, 175, 80, 0.05);">
      <h3 style="color: #4CAF50;">🏗️ Multi-Tier Architecture</h3>
      <p>Progressive complexity from Oracles to Sovereigns with built-in safety. Free tiers (Oracle & Genie) and commercial tiers for enterprise.</p>
    </td>
  </tr>
</table>

## 🌟 How SuperOptiX Differs from Other Frameworks

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Feature</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Other Frameworks</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">SuperOptiX</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🎯 Evaluation-First</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Add evaluation as an afterthought</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">Evaluation built into core development cycle ✅</strong></td>
  </tr>
  <tr style="background: rgba(33, 150, 243, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>✅ RSpec-Style BDD Development</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Manual prompt engineering</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #2196F3;">Behavior-driven specifications with automated testing ✅</strong></td>
  </tr>
  <tr style="background: rgba(255, 152, 0, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🧬 Universal GEPA Optimizer</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Manual optimization or framework-specific tools</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #FF9800;">One optimizer for all frameworks (37.5% → 80% improvement) ✅</strong></td>
  </tr>
  <tr style="background: rgba(156, 39, 176, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🔬 Multi-Framework Freedom</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Locked into one approach</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #9C27B0;">Choose from 6 frameworks, optimize with one tool ✅</strong></td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🚀 Production-Ready</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Basic deployment capabilities</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">Built-in observability, guardrails, and enterprise features ✅</strong></td>
  </tr>
</table>

## Multi-Framework Support: Choose Your Tool, Keep Your Workflow

SuperOptiX is the **world's first framework-agnostic agent optimizer**. Build agents in any of the 6 major frameworks, then optimize them all with the same powerful GEPA engine.

### 🔬 Supported Frameworks

<table style="width: 100%; border-collapse: collapse; margin: 20px 0; text-align: center;">
  <tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Framework</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Variables</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Local Models</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Best For</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Status</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🔬 DSPy</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">10+</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">✅ Ollama</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Complex reasoning, research</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">Proven: 37.5% → 80%</strong></td>
  </tr>
  <tr style="background: rgba(33, 150, 243, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🤖 OpenAI SDK</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">1</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">✅ Ollama</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Simple & fast</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #2196F3;">Proven: 100% pass rate</strong></td>
  </tr>
  <tr style="background: rgba(255, 152, 0, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>👥 CrewAI</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">5</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">✅ Ollama</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Multi-agent teams</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #FF9800;">Proven: 100% pass rate</strong></td>
  </tr>
  <tr style="background: rgba(128, 128, 128, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🔮 Google ADK</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">1</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">☁️ Cloud</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Gemini native, free tier</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Ready</td>
  </tr>
  <tr style="background: rgba(128, 128, 128, 0.08);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🏢 Microsoft</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">1</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">✅ Ollama</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Enterprise Azure</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Ready</td>
  </tr>
  <tr style="background: rgba(128, 128, 128, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🌊 DeepAgents</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">1</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">✅ Ollama</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Complex planning</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Ready</td>
  </tr>
</table>

### One Workflow, All Frameworks

```bash
# Same workflow regardless of framework!
super agent compile my_agent --framework [dspy|openai|crewai|google-adk|microsoft|deepagents]
super agent evaluate my_agent
super agent optimize my_agent --auto medium  # GEPA works on ALL frameworks
super agent run my_agent
```

!!! tip "Learn More"
    See our [Multi-Framework Support Guide](guides/multi-framework.md) for detailed comparisons and examples.

## Universal Workflow

SuperOptiX provides a consistent workflow across all frameworks:

1. **Specify**: Define your agent using SuperSpec DSL
2. **Compile**: Generate framework-specific code
3. **Evaluate**: Test with RSpec-style BDD scenarios
4. **Optimize**: Improve with GEPA
5. **Deploy**: Run in production

```bash
# Initialize project
super init my_project
cd my_project

# Pull a pre-built agent
super agent pull sentiment_analyzer

# Compile for your chosen framework
super agent compile sentiment_analyzer

# Evaluate performance
super agent evaluate sentiment_analyzer

# Optimize with GEPA
super agent optimize sentiment_analyzer --auto medium

# Run in production
super agent run sentiment_analyzer
```

## Architecture Overview

SuperOptiX consists of several key components:

- **SuperSpec DSL**: Declarative specification language
- **GEPA Optimizer**: Universal optimization engine
- **Framework Adapters**: Support for 6 major frameworks
- **Evaluation Engine**: RSpec-style BDD testing framework
- **Memory System**: Multi-layered memory management
- **RAG Integration**: Knowledge retrieval across frameworks
- **Orchestra**: Multi-agent coordination
- **Observability**: Built-in monitoring and tracing

## 📈 Proven Results

GEPA has delivered dramatic improvements across all tested frameworks:

<table style="width: 100%; border-collapse: collapse; margin: 20px 0; text-align: center;">
  <tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Framework</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Baseline</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">After GEPA</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Improvement</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🔬 DSPy</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">37.5%</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">80.0%</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">+42.5 pts 🏆</strong></td>
  </tr>
  <tr style="background: rgba(33, 150, 243, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🤖 OpenAI SDK</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">100%</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">100%</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #2196F3;">Maintained ✅</strong></td>
  </tr>
  <tr style="background: rgba(255, 152, 0, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>👥 CrewAI</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">75%</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">100%</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #FF9800;">+25 pts ⭐</strong></td>
  </tr>
  <tr style="background: rgba(128, 128, 128, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🔮 Google ADK</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);" colspan="3"><em>Ready for optimization</em></td>
  </tr>
  <tr style="background: rgba(128, 128, 128, 0.08);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🏢 Microsoft</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);" colspan="3"><em>Ready for optimization</em></td>
  </tr>
  <tr style="background: rgba(128, 128, 128, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong>🌊 DeepAgents</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);" colspan="3"><em>Ready for optimization</em></td>
  </tr>
</table>

!!! success "Sample Efficient"
    GEPA achieves these improvements with just 3-10 training scenarios, while traditional methods require hundreds of examples.

## 🚀 Getting Started

Ready to build your first optimized agent?

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
  <tr>
    <td style="padding: 20px; text-align: center; width: 20%; border: 2px solid rgba(76, 175, 80, 0.3); background: rgba(76, 175, 80, 0.05);">
      <h2>1️⃣</h2>
      <h4><a href="../quick-start/" style="color: #4CAF50; text-decoration: none; font-weight: bold;">Quick Start Guide</a></h4>
      <p>Build your first agent in 10 minutes</p>
    </td>
    <td style="padding: 20px; text-align: center; width: 20%; border: 2px solid rgba(33, 150, 243, 0.3); background: rgba(33, 150, 243, 0.05);">
      <h2>2️⃣</h2>
      <h4><a href="../setup/" style="color: #2196F3; text-decoration: none; font-weight: bold;">Installation</a></h4>
      <p>Set up your development environment</p>
    </td>
    <td style="padding: 20px; text-align: center; width: 20%; border: 2px solid rgba(255, 152, 0, 0.3); background: rgba(255, 152, 0, 0.05);">
      <h2>3️⃣</h2>
      <h4><a href="../llm-setup/" style="color: #FF9800; text-decoration: none; font-weight: bold;">LLM Setup</a></h4>
      <p>Configure your language models</p>
    </td>
    <td style="padding: 20px; text-align: center; width: 20%; border: 2px solid rgba(156, 39, 176, 0.3); background: rgba(156, 39, 176, 0.05);">
      <h2>4️⃣</h2>
      <h4><a href="../guides/superspec/" style="color: #9C27B0; text-decoration: none; font-weight: bold;">SuperSpec Guide</a></h4>
      <p>Learn the specification language</p>
    </td>
    <td style="padding: 20px; text-align: center; width: 20%; border: 2px solid rgba(76, 175, 80, 0.3); background: rgba(76, 175, 80, 0.05);">
      <h2>5️⃣</h2>
      <h4><a href="../guides/gepa-optimization/" style="color: #4CAF50; text-decoration: none; font-weight: bold;">GEPA Optimization</a></h4>
      <p>Master universal optimization</p>
    </td>
  </tr>
</table>

## 🏗️ Progressive Tier System

SuperOptiX offers a progressive architecture from simple to enterprise complexity:

<table style="width: 100%; border-collapse: collapse; margin: 20px 0; text-align: center;">
  <tr style="background: rgba(33, 150, 243, 0.15); font-weight: bold;">
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Tier</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Description</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Cost</td>
    <td style="padding: 15px; border: 2px solid rgba(128, 128, 128, 0.3);">Status</td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.08);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">🧙‍♂️ Oracles</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Simple Q&A agents</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">🆓 Free</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">✅ Available</strong></td>
  </tr>
  <tr style="background: rgba(76, 175, 80, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">🧞‍♂️ Genies</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Multi-step reasoning with tools & RAG</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">🆓 Free</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #4CAF50;">✅ Available</strong></td>
  </tr>
  <tr style="background: rgba(255, 152, 0, 0.08);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #FF9800;">🎭 Protocols</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">MCP & A2A support, advanced workflows</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #FF9800;">💼 Commercial</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #FF9800;">🔒 Available</strong></td>
  </tr>
  <tr style="background: rgba(255, 152, 0, 0.05);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #FF9800;">🤖 Superagents</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Multi-agent coordination systems</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #FF9800;">💼 Commercial</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">In Progress</td>
  </tr>
  <tr style="background: rgba(156, 39, 176, 0.08);">
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #9C27B0;">👑 Sovereigns</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Autonomous AI for large-scale operations</td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);"><strong style="color: #9C27B0;">💼 Commercial</strong></td>
    <td style="padding: 12px; border: 2px solid rgba(128, 128, 128, 0.3);">Coming Soon</td>
  </tr>
</table>

!!! info "Free Tiers Available"
    Oracle and Genie tiers are completely free to try, no credit card required!

<div align="center" style="margin: 30px 0;">
  <a href="../guides/tiers/" style="background: #4CAF50; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; margin: 5px; display: inline-block; font-weight: bold;">🎭 View Full Tier Details</a>
</div>

## Community and Support

- **Documentation**: [https://superoptix.ai/docs](https://superoptix.ai/docs)
- **GitHub**: [https://github.com/SuperagenticAI/SuperOptiX](https://github.com/SuperagenticAI/SuperOptiX)
- **Website**: [https://superoptix.ai](https://superoptix.ai)

## 🎯 Next Steps

<table style="width: 100%; border-collapse: collapse;">
  <tr>
    <td style="padding: 20px; text-align: center; width: 25%; border: 2px solid rgba(76, 175, 80, 0.3); background: rgba(76, 175, 80, 0.05);">
      <h2>🚀</h2>
      <h4><a href="../quick-start/" style="color: #4CAF50; text-decoration: none; font-weight: bold;">Quick Start</a></h4>
      <p>Build your first agent in 10 minutes</p>
    </td>
    <td style="padding: 20px; text-align: center; width: 25%; border: 2px solid rgba(33, 150, 243, 0.3); background: rgba(33, 150, 243, 0.05);">
      <h2>📚</h2>
      <h4><a href="../guides/" style="color: #2196F3; text-decoration: none; font-weight: bold;">Guides</a></h4>
      <p>In-depth tutorials and guides</p>
    </td>
    <td style="padding: 20px; text-align: center; width: 25%; border: 2px solid rgba(255, 152, 0, 0.3); background: rgba(255, 152, 0, 0.05);">
      <h2>⚙️</h2>
      <h4><a href="../reference/api/" style="color: #FF9800; text-decoration: none; font-weight: bold;">API Reference</a></h4>
      <p>Complete API documentation</p>
    </td>
    <td style="padding: 20px; text-align: center; width: 25%; border: 2px solid rgba(156, 39, 176, 0.3); background: rgba(156, 39, 176, 0.05);">
      <h2>💡</h2>
      <h4><a href="../examples/" style="color: #9C27B0; text-decoration: none; font-weight: bold;">Examples</a></h4>
      <p>Real-world agent examples</p>
    </td>
  </tr>
</table>

---

<div align="center" style="margin: 40px 0;">
  <h2>🚀 Ready to Build Optimized AI Agents?</h2>
  <p style="font-size: 1.2em; margin: 20px 0;">Start with our free Oracle & Genie tiers today!</p>
</div>

<div align="center" style="margin: 30px 0;">
  <a href="../quick-start/" style="background: #4CAF50; color: white; padding: 16px 32px; text-decoration: none; border-radius: 4px; margin: 10px; display: inline-block; font-weight: bold; font-size: 1.1em;">🚀 Start Free</a>
  <a href="../tutorials/oracles-agent/" style="background: #2196F3; color: white; padding: 16px 32px; text-decoration: none; border-radius: 4px; margin: 10px; display: inline-block; font-weight: bold; font-size: 1.1em;">🤖 Create First Agent</a>
  <a href="../guides/tiers/" style="background: #FF9800; color: white; padding: 16px 32px; text-decoration: none; border-radius: 4px; margin: 10px; display: inline-block; font-weight: bold; font-size: 1.1em;">🎭 View All Tiers</a>
</div>
