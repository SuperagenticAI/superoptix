# ❓ Frequently Asked Questions

## Framework Overview

### What does SuperOptiX do?

SuperOptiX gives an agent you already run an A2A interface, and then measures whether other
agents actually find it.

There are two halves. The first is adaptation: point `super a2a adapt` at an entrypoint, and
SuperOptiX reads the agent's structure, derives the skills a calling agent would route on, and
writes an Agent Card plus a conformant server. Your agent code is not modified. The second is
routing quality: an Agent Card is a routing surface, and the wording of its skill descriptions
decides whether a caller picks your agent or a different one. SuperOptiX scores that and
improves it with GEPA.

SuperOptiX also compiles agents from SuperSpec, a declarative YAML format, into native code for
any supported runtime.

### Which runtimes are supported?

DSPy, CrewAI, the OpenAI Agents SDK, Pydantic AI, Google ADK, the Claude Agent SDK, DeepAgents
and the Microsoft Agent Framework. Adaptation works on agents written directly against those
libraries, whether or not SuperOptiX built them.

### Is this an agent framework?

SuperOptiX is a layer over the framework you chose. It does not ask you to move your agent onto
a new runtime, and it does not sit in the request path once the server is generated. The
generated server is a standalone FastAPI application you deploy however you deploy anything else.

### How does SuperOptiX relate to DSPy?

DSPy is one of the eight supported runtimes, and it is also the optimization engine behind the
`--optimize` path and the routing work. Agents on the other seven runtimes are adapted and
optimized without DSPy being involved in their execution.

### Is SuperOptiX just a DSPy wrapper?

No. Adaptation reads the structure of CrewAI crews, ADK agents, Pydantic AI agents and the rest
through per-runtime introspectors that have nothing to do with DSPy. The parts that touch DSPy
are the compile path and the optimizers.

### Can SuperOptiX work with other optimization frameworks?

The optimizer layer is pluggable. GEPA is the default for routing work because it optimizes
free-form text against a scoring function, which is what a skill description needs. DSPy
optimizers cover the pipeline compile path. Adding a backend means implementing the optimizer
interface.

## A2A

### How conformant is the A2A implementation?

Zero failures against the official A2A Technology Compatibility Kit. Every requirement the TCK
exercises against the conformance harness passes: 73 of 73 at MUST, 7 of 7 at SHOULD, 4 of 4 at MAY.

The TCK also prints a headline percentage, currently 77.7% at MUST. That counts 25 requirements
it cannot exercise here as non-compliant, covering authentication and TLS, Agent Card JWS
signatures, cross-binding equivalence, version negotiation probes and the gRPC binding. Those
features are not implemented, so the TCK has nothing to test. See
[A2A conformance](guides/a2a-conformance.md).

### Is A2A a paid feature?

No. The A2A implementation, the adapt command, the conformance suite and the routing optimizer
are all in the MIT-licensed package.

### Is there a live endpoint I can call?

Yes. A SuperOptiX agent runs at `https://a2a.superoptix.ai`, and its Agent Card is published at
`https://superoptix.ai/.well-known/agent-card.json`.

```bash
curl -X POST https://a2a.superoptix.ai/message:send \
  -H 'content-type: application/json' \
  -d '{"message":{"role":"ROLE_USER","parts":[{"text":"Does CrewAI support A2A?"}]}}'

curl -X POST https://a2a.superoptix.ai/a2a/jsonrpc \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{"role":"user","parts":[{"kind":"text","text":"Does CrewAI support A2A?"}]}}}'
```

The agent answers from a static table of runtime capabilities. It does not call a model.

### Which A2A version does it serve?

Both 1.0 and 0.3, from the same endpoint. The version is negotiated per request, so a 0.3 client
and a 1.0 client can call the same agent.

### Do I have to rewrite my agent?

No. `super a2a adapt` imports your entrypoint, reads its structure, and writes the Agent Card and
server alongside it. The files it writes are ordinary Python and JSON that you can edit.

### What does routing optimization actually change?

The text in the Agent Card: skill names, descriptions and tags. The agent's behaviour is
untouched. The measurement is a set of queries scored for discovery rate, invocation rate and
confusion rate. See [Routing quality](guides/a2a-routing.md).

## Licensing

### Is SuperOptiX open source?

Yes, under the MIT License. The A2A protocol implementation, the adapt command, the conformance
suite, the routing optimizer, the SuperSpec compiler and all eight runtime integrations are in
the open source package.

### What are Oracle and Genie tiers?

They describe agent capability in a SuperSpec, not a license level. Oracle agents answer from the
model alone. Genie agents add tools, retrieval, memory and streaming. Both are in the open source
package, and `super agent pull` will fetch either.

### Does Superagentic AI offer anything commercially?

Superagentic AI offers support and custom engagements. Contact them for details. Nothing in this
repository is gated behind that.

## 🔧 **Installation & Dependencies**

### Can I install CrewAI alongside SuperOptiX?

Yes, as a separate step. CrewAI is left out of the `frameworks` extra because it requires
`chromadb~=1.1.0`, while the `chromadb`, `turboagents` and `vectordb` extras require
`chromadb>=1.5.5`.

```bash
uv pip install superoptix "crewai>=1.15"
```

Use an environment without the `turboagents` or `vectordb` extras for that path.

The `json-repair` conflict documented in older versions of this page is resolved upstream.
CrewAI 1.15 and DSPy 3.3 agree on `json-repair` and co-install cleanly.

### How large is the install?

The base package is around 220MB. PyTorch, Transformers and Accelerate are not core
dependencies; install `superoptix[huggingface]` if you want the local Hugging Face backend.

## 🎓 **Learning & Usage**

### Do I need to know DSPy to use SuperOptiX?

**Not necessarily, but it helps:**

- **🛡️ SuperOptiX handles DSPy complexity** - The framework abstracts most DSPy internals
- **🚀 You can start immediately** - Basic agents work out-of-the-box with minimal DSPy knowledge
- **🎯 DSPy knowledge = Full control** - Understanding DSPy helps you create production-worthy pipelines
- **📚 Learning path** - Start with SuperOptiX basics, then learn DSPy for advanced customization

**💡 Recommendation:** Start with SuperOptiX's high-level APIs, then learn DSPy as you need more control over optimization and pipeline design.

## ⚡ **Optimization & Performance**

### What optimization strategies does SuperOptiX support?

SuperOptiX provides multiple optimization strategies:

- **🎯 BootstrapFewShot** - Automatic few-shot learning with bootstrapped demonstrations
- **🔄 ReAct** - Reasoning and acting optimization for tool-using agents
- **📊 Multi-Metric Optimization** - Optimize for multiple metrics simultaneously
- **Tier-Specific Optimization** - Different strategies for Oracle and Genie agents
- **🛠️ Tool-Aware Optimization** - Optimization that considers tool usage patterns

### Can I optimize agents for specific use cases?

**Yes, absolutely:**

- **🎯 Custom Evaluation Metrics** - Define domain-specific evaluation criteria
- **📊 BDD Scenarios** - Create executable specifications for your use case
- **🛠️ Tool Integration** - Optimize for specific tool usage patterns
- **🧠 Memory Optimization** - Tune memory systems for your data patterns
- **📈 Performance Profiling** - Identify and optimize bottlenecks

## 🧪 **Evaluation & Testing**

### How does SuperOptiX's evaluation system work?

The evaluation system provides:

- **🎯 BDD/TDD Approach** - Executable specifications as test cases
- **📊 Multiple Metrics** - Semantic F1, exact match, reasoning quality, tool efficiency
- **🔄 Continuous Evaluation** - Automated testing in CI/CD pipelines
- **📈 Quality Gates** - Pass/fail thresholds for automated deployment
- **🎭 Scenario Testing** - Complex multi-step scenario validation

### What evaluation metrics are available?

SuperOptiX includes:

- **🎯 Semantic F1** - Semantic similarity scoring
- **Exact Match** - Precise answer matching
- **🧠 Reasoning Quality** - Assessment of reasoning process
- **🛠️ Tool Usage Efficiency** - Evaluation of tool selection and usage
- **📊 Response Time** - Performance and latency metrics
- **💰 Cost Metrics** - Token usage and cost tracking
- **🎭 Custom Metrics** - Domain-specific evaluation criteria

### How do I set up automated testing?

The framework provides:

- **🔄 CI/CD Integration** - GitHub Actions, GitLab CI, Jenkins, Azure DevOps
- **📊 Quality Gates** - Automated pass/fail thresholds
- **🎯 BDD Scenarios** - Executable specifications as tests
- **📈 Performance Monitoring** - Continuous performance tracking
- **🚀 Automated Deployment** - Deploy only when tests pass

## 🧠 **Memory Systems**

### What types of memory does SuperOptiX support?

The framework provides three memory layers:

- **📝 Episodic Memory** - Conversation history and interaction episodes
- **🧠 Semantic Memory** - Persistent knowledge and relationships
- **⚡ Working Memory** - Temporary session information

### What storage backends are available?

SuperOptiX supports multiple backends:

- **🗄️ SQLite** - Lightweight, file-based storage (default)
- **🔴 Redis** - High-performance, in-memory storage
- **📁 File** - Simple file-based storage with JSON/YAML formats

### How does memory integration work?

Memory integration provides:

- **🎯 Context Retrieval** - Automatic relevant context for responses
- **📊 Memory Statistics** - Usage tracking and analytics
- **🔄 Automatic Cleanup** - Retention policies and cleanup
- **🧠 Semantic Search** - Find relevant memories by content
- **⚡ Working Memory** - Temporary data with TTL support

## Tools

### What tools are included?

The tool registry ships 17 tools across four categories: Core (web search, calculator, file
reader, datetime, text analyzer, JSON processor), Development (git analyzer, API tester, code
formatter, code reviewer, test coverage, dependency analyzer, version checker, Docker helper,
database query), Data (data processor) and Miscellaneous (SurrealDB query). Browse them with
`super marketplace browse categories`.

A further 95 industry tool classes live in `superoptix.tools.categories`, covering agriculture,
education, energy, finance, gaming and sports, healthcare, hospitality, human resources, legal,
manufacturing, marketing, real estate, retail, transportation and utilities. Those are imported
directly rather than resolved through the registry:

```python
from superoptix.tools.categories.finance import CurrencyConverterTool
```

Some of them, including the currency converter, return sample data rather than calling a live
service. Read the tool before relying on its numbers.

### Can I create custom tools?

Yes. Inherit from `BaseTool`, or use the factories in `superoptix.tools.factories`. Parameter
schemas are validated, and the registry discovers tools by category.

---

Further reading: [documentation](index.md), [guides](guides/index.md), or [support@superagentic.ai](mailto:support@superagentic.ai). 